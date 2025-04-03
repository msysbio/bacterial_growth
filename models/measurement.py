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
from models.measurement_technique import TECHNIQUE_NAMES
from db import get_session
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
        from models import (
            Metabolite,
            Strain,
            Bioreplicate,
        )

        with get_session() as db_session:
            if subject_type == 'metabolite':
                return db_session.get(Metabolite, subject_id)
            elif subject_type == 'strain':
                return db_session.get(Strain, subject_id)
            elif subject_type == 'bioreplicate':
                return db_session.get(Bioreplicate, subject_id)

    def subject_join(subject_type):
        from models import (
            Metabolite,
            Strain,
            Bioreplicate,
        )

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
    def insert_from_bioreplicates_csv(Self, db_session, study, csv_string):
        from models import Bioreplicate

        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study.studyId, bioreplicate_id)

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            for technique in study.measurementTechniques:
                if technique.subjectType != 'bioreplicate':
                    continue

                technique_name = TECHNIQUE_NAMES[technique.type]
                value = row[technique_name]
                if value == '':
                    value = None
                units = technique.units

                time_in_seconds = convert_time(row['Time'], source=study.timeUnits, target='s')

                measurement = Self(
                    studyId=study.studyId,
                    bioreplicateUniqueId=bioreplicate_uuid,
                    position=row['Position'],
                    timeInSeconds=time_in_seconds,
                    unit=units,
                    techniqueId=technique.id,
                    technique=_generate_technique_name(technique.type, technique.subjectType),
                    value=value,
                    subjectId=bioreplicate_uuid,
                    subjectType='bioreplicate',
                )
                measurements.append(measurement)

        db_session.add_all(measurements)
        db_session.commit()

        return measurements

    @classmethod
    def insert_from_strain_csv(Self, db_session, study, csv_string):
        from models import Bioreplicate

        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study.studyId, bioreplicate_id)

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            for technique in study.measurementTechniques:
                if technique.subjectType != 'strain':
                    continue

                if technique.type == '16s':
                    suffix = 'rRNA reads'
                elif technique.type == 'fc':
                    suffix = 'FC counts'
                elif technique.type == 'plates':
                    suffix = 'plate counts'
                else:
                    raise ValueError(f"Unexpected technique type: {technique.type}")

                for subject in study.strains:
                    value = row[f"{subject.name} {suffix}"]
                    if value == '':
                        value = None
                    units = technique.units

                    time_in_seconds = convert_time(row['Time'], source=study.timeUnits, target='s')

                    measurement = Self(
                        studyId=study.studyId,
                        bioreplicateUniqueId=bioreplicate_uuid,
                        position=row['Position'],
                        timeInSeconds=time_in_seconds,
                        unit=units,
                        technique=_generate_technique_name(technique.type, technique.subjectType),
                        techniqueId=technique.id,
                        value=value,
                        subjectId=subject.id,
                        subjectType='strain',
                    )
                    measurements.append(measurement)

        db_session.add_all(measurements)
        db_session.commit()

        return measurements

    @classmethod
    def insert_from_metabolites_csv(Self, db_session, study, csv_string):
        from models import (
            Bioreplicate,
            Metabolite,
            StudyMetabolite,
        )

        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        # TODO (2025-04-03) Figure out how to make a many-to-many relationship
        metabolites = db_session.scalars(
            sql.select(Metabolite)
            .join(StudyMetabolite)
            .where(StudyMetabolite.studyId == study.studyId)
        ).all()

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study.studyId, bioreplicate_id)

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            for technique in study.measurementTechniques:
                if technique.subjectType != 'metabolite':
                    continue

                for subject in metabolites:
                    value = row[subject.name]
                    if value == '':
                        value = None
                    units = technique.units

                    time_in_seconds = convert_time(row['Time'], source=study.timeUnits, target='s')

                    measurement = Self(
                        studyId=study.studyId,
                        bioreplicateUniqueId=bioreplicate_uuid,
                        position=row['Position'],
                        timeInSeconds=time_in_seconds,
                        unit=units,
                        techniqueId=technique.id,
                        technique=_generate_technique_name(technique.type, technique.subjectType),
                        value=value,
                        subjectId=subject.id,
                        subjectType='metabolite',
                    )
                    measurements.append(measurement)

        db_session.add_all(measurements)
        db_session.commit()

        return measurements


def _generate_technique_name(technique_type, subject_type):
    match (technique_type.lower(), subject_type):
        case ('fc', 'bioreplicate'):
            return 'FC'
        case ('fc', 'strain'):
            return 'FC counts per species'
        case ('metabolite', _):
            return 'Metabolites'
        case ('16s', _):
            return '16S rRNA-seq'
        case ('ph', _):
            return 'pH'
        case ('od', _):
            return 'OD'
        case _:
            raise ValueError(f"Unknown technique name for type {technique_type}, subject {subject_type}")
