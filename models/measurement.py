from io import StringIO
import csv
import functools
from decimal import Decimal

import sqlalchemy as sql
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
    aliased,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase
from lib.conversion import convert_time
from lib.util import group_by_unique_name


class Measurement(OrmBase):
    __tablename__ = "Measurements"

    id: Mapped[int] = mapped_column(primary_key=True)

    bioreplicateUniqueId: Mapped[int] = mapped_column(sql.ForeignKey('Bioreplicates.id'))
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurements')

    compartmentId: Mapped[int] = mapped_column(sql.ForeignKey('Compartments.id'))
    compartment: Mapped['Compartment'] = relationship(back_populates='measurements')

    # TODO (2025-04-24) Use unique id
    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates="measurements")

    timeInSeconds: Mapped[int] = mapped_column(sql.Integer,     nullable=False)
    unit:          Mapped[str] = mapped_column(sql.String(100), nullable=False)

    # Should be removed at some point
    technique: Mapped[str] = mapped_column(sql.String(100))

    # TODO (2025-03-30) This should not be nullable, but we need to migrate the data first
    techniqueId: Mapped[int] = mapped_column(sql.ForeignKey("MeasurementTechniques.id"))

    # TODO (2025-04-06) Remove the string `technique` or rename to `technique_name`
    techniqueRecord: Mapped['MeasurementTechnique'] = relationship(
        back_populates="measurements"
    )

    value: Mapped[Decimal] = mapped_column(sql.Numeric(20, 2), nullable=True)
    std:   Mapped[Decimal] = mapped_column(sql.Numeric(20, 2), nullable=True)

    subjectId:   Mapped[str] = mapped_column(sql.String(100), nullable=False)
    subjectType: Mapped[str] = mapped_column(sql.String(100), nullable=False)

    @hybrid_property
    def timeInHours(self):
        return self.timeInSeconds / 3600

    @classmethod
    def get_subject(Self, db_session, subject_id, subject_type):
        from models import Metabolite, Strain, Bioreplicate

        if subject_type == 'metabolite':
            return db_session.get(Metabolite, subject_id)
        elif subject_type == 'strain':
            return db_session.get(Strain, subject_id)
        elif subject_type == 'bioreplicate':
            return db_session.get(Bioreplicate, subject_id)
        else:
            raise ValueError(f"Unknown subject type: {subject_type}")

    def subject_join(subject_type):
        from models import Metabolite, Strain, Bioreplicate

        if subject_type == 'metabolite':
            Subject = Metabolite
        elif subject_type == 'strain':
            Subject = Strain
        elif subject_type == 'bioreplicate':
            Subject = aliased(Bioreplicate)

        name = Subject.name.label("subjectName")
        join = (Subject, Measurement.subjectId == Subject.id)

        return (name, join)

    @classmethod
    def insert_from_csv_string(Self, db_session, study, csv_string, subject_type):
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        bioreplicates_by_name = group_by_unique_name(study.bioreplicates)
        compartments_by_name  = group_by_unique_name(study.compartments)

        measurements = []

        for row in reader:
            bioreplicate = bioreplicates_by_name[row['Biological Replicate'].strip()]
            compartment  = compartments_by_name[row['Compartment'].strip()]

            if bioreplicate is None or compartment is None:
                # Missing entry, skip
                continue

            time_in_seconds = convert_time(row['Time'], source=study.timeUnits, target='s')

            for technique in study.measurementTechniques:
                if technique.subjectType != subject_type:
                    continue

                if subject_type == 'bioreplicate':
                    subjects = [bioreplicate]
                elif subject_type == 'strain':
                    subjects = study.strains
                elif subject_type == 'metabolite':
                    subjects = study.metabolites
                else:
                    raise KeyError(f"Unexpected subject type: {subject_type}")

                for subject in subjects:
                    value_column_name = technique.csv_column_name(subject.name)

                    value = row[value_column_name]
                    if value == '':
                        value = None

                    std = row.get(f"{value_column_name} STD", None)
                    if std == '':
                        std = None

                    measurement = Measurement(
                        # Relationships:
                        study=study,
                        bioreplicate=bioreplicate,
                        compartment=compartment,
                        # Subject:
                        subjectId=subject.id,
                        subjectType=subject_type,
                        # Technique:
                        techniqueId=technique.id,
                        technique=_generate_technique_name(technique.type, technique.subjectType),
                        # Data:
                        timeInSeconds=time_in_seconds,
                        value=value,
                        std=std,
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
