from io import StringIO
import csv
import functools
from decimal import Decimal

from sqlalchemy import (
    Integer,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    aliased,
)
from sqlalchemy.ext.hybrid import hybrid_property
import sqlalchemy as sql

from models.orm_base import OrmBase
from models.bioreplicate import Bioreplicate
from models.strain import Strain
from models.metabolite import Metabolite
from models.measurement_technique import TECHNIQUE_NAMES
from db import get_session
from lib.db import execute_text
from lib.conversion import convert_time


class Measurement(OrmBase):
    __tablename__ = "Measurements"

    id: Mapped[int] = mapped_column(primary_key=True)

    bioreplicateUniqueId: Mapped[int] = mapped_column(
        ForeignKey('BioReplicatesPerExperiment.bioreplicateUniqueId'),
    )
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurements')

    # Note: should be a ForeignKey + relationship. However, ORM model is not
    # defined yet.
    studyId: Mapped[str] = mapped_column(String(100), nullable=False)

    position:      Mapped[str] = mapped_column(String(100), nullable=False)
    timeInSeconds: Mapped[int] = mapped_column(Integer,     nullable=False)
    pH:            Mapped[str] = mapped_column(String(100), nullable=False)
    unit:          Mapped[str] = mapped_column(String(100), nullable=False)

    # Should be removed at some point
    technique: Mapped[str] = mapped_column(String(100))

    # TODO (2025-03-30) This should not be nullable, but we need to migrate the data first
    techniqueId: Mapped[int] = mapped_column(ForeignKey("MeasurementTechniques.id"))

    value: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=True)
    std:   Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=True)

    subjectId:   Mapped[str] = mapped_column(String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(String(100), nullable=False)

    @hybrid_property
    def timeInHours(self):
        return self.timeInSeconds / 3600

    @classmethod
    def get_subject(Self, subject_id, subject_type):
        with get_session() as db_session:
            if subject_type == 'metabolite':
                return db_session.get(Metabolite, subject_id)
            elif subject_type == 'strain':
                return db_session.get(Strain, subject_id)
            elif subject_type == 'bioreplicate':
                return db_session.get(Bioreplicate, subject_id)

    def subject_join(subject_type):
        if subject_type == 'metabolite':
            name = Metabolite.metabo_name.label("subjectName")
            join = (Metabolite, Measurement.subjectId == Metabolite.id)
        elif subject_type == 'strain':
            name = Strain.memberName.label("subjectName")
            join = (Strain, Measurement.subjectId == Strain.strainId)
        elif subject_type == 'bioreplicate':
            name = Bioreplicate.bioreplicateId.label("subjectName")
            Subject = aliased(Bioreplicate)
            join = (Subject, Measurement.subjectId == Subject.bioreplicateUniqueId)

        return (name, join)

    @classmethod
    def insert_from_bioreplicates_csv(Self, db_session, study_id, time_units, techniques, csv_string):
        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study_id, bioreplicate_id)

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            for technique in techniques:
                technique_name = TECHNIQUE_NAMES[technique.type]
                value = row[technique_name]
                units = technique.units

                time_in_seconds = convert_time(row['Time'], source=time_units, target='s')

                measurements.append(Self(
                    studyId=study_id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                    position=row['Position'],
                    timeInSeconds=time_in_seconds,
                    unit=units,
                    techniqueId=technique.id,
                    value=value,
                    subjectId=bioreplicate_uuid,
                    subjectType='bioreplicate',
                ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements

    @classmethod
    def insert_from_metabolites_csv(Self, db_session, study_id, time_units, techniques, csv_string):
        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study_id, bioreplicate_id)

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            for technique in techniques:
                subjects = db_session.scalars(
                    sql.select(Metabolite)
                    .where(Metabolite.id.in_(technique.metaboliteIds))
                )

                for subject in subjects:
                    value = row[f"{subject.name} ({technique.units})"]
                    if value == '':
                        value = None
                    units = technique.units

                    time_in_seconds = convert_time(row['Time'], source=time_units, target='s')

                    measurements.append(Self(
                        studyId=study_id,
                        bioreplicateUniqueId=bioreplicate_uuid,
                        position=row['Position'],
                        timeInSeconds=time_in_seconds,
                        unit=units,
                        techniqueId=technique.id,
                        value=value,
                        subjectId=subject.id,
                        subjectType='metabolite',
                    ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements

    @classmethod
    def insert_from_strain_csv(Self, db_session, study_id, time_units, techniques, csv_string):
        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study_id, bioreplicate_id)

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            for technique in techniques:
                if technique.type == '16s':
                    suffix = 'reads'
                else:
                    suffix = f"{TECHNIQUE_NAMES[technique.type]} ({technique.units})"

                subjects = db_session.scalars(
                    sql.select(Strain)
                    .where(Strain.id.in_(technique.strainIds))
                )

                for subject in subjects:
                    value = row[f"{subject.name} {suffix}"]
                    if value == '':
                        value = None
                    units = technique.units

                    time_in_seconds = convert_time(row['Time'], source=time_units, target='s')

                    measurements.append(Self(
                        studyId=study_id,
                        bioreplicateUniqueId=bioreplicate_uuid,
                        position=row['Position'],
                        timeInSeconds=time_in_seconds,
                        unit=units,
                        techniqueId=technique.id,
                        value=value,
                        subjectId=subject.id,
                        subjectType='strain',
                    ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements
