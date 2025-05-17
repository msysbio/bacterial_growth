import csv
from io import StringIO
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

    # A relationship that goes through the parent measurement context:
    context_relationship = lambda: relationship(
        secondary='MeasurementContexts',
        viewonly=True,
    )

    id: Mapped[int] = mapped_column(primary_key=True)

    studyId: Mapped[str] = mapped_column(sql.ForeignKey('Study.studyId'), nullable=False)
    study: Mapped['Study'] = relationship(back_populates='measurements')

    contextId: Mapped[int] = mapped_column(sql.ForeignKey('MeasurementContexts.id'))
    context: Mapped['MeasurementContext'] = relationship(back_populates='measurements')

    bioreplicate: Mapped['Bioreplicate']         = context_relationship()
    compartment:  Mapped['Compartment']          = context_relationship()
    technique:    Mapped['MeasurementTechnique'] = context_relationship()

    timeInSeconds: Mapped[int] = mapped_column(sql.Integer,     nullable=False)

    value: Mapped[Decimal] = mapped_column(sql.Numeric(20, 2), nullable=True)
    std:   Mapped[Decimal] = mapped_column(sql.Numeric(20, 2), nullable=True)

    @hybrid_property
    def timeInHours(self):
        return self.timeInSeconds / 3600

    @hybrid_property
    def subjectId(self):
        return self.context.subjectId

    @hybrid_property
    def subjectType(self):
        return self.context.subjectType

    @classmethod
    def insert_from_csv_string(Self, db_session, study, csv_string, subject_type):
        from models import MeasurementContext

        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        bioreplicates_by_name = group_by_unique_name(study.bioreplicates)
        compartments_by_name  = group_by_unique_name(study.compartments)
        context_cache = {}

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
                    # Create a measurement context only if it doesn't already exist:
                    context_key = (bioreplicate.id, compartment.id, technique.id, subject.id, subject_type)
                    if context_key not in context_cache:
                        if subject_type == 'metabolite':
                            subjectId = subject.chebiId
                        else:
                            subjectId = subject.id

                        context = MeasurementContext(
                            # Relationships:
                            study=study,
                            bioreplicate=bioreplicate,
                            compartment=compartment,
                            # Subject:
                            subjectId=subjectId,
                            subjectType=subject_type,
                            # Technique:
                            techniqueId=technique.id,
                        )
                        context_cache[context_key] = context
                        db_session.add(context)

                    context = context_cache[context_key]
                    value_column_name = technique.csv_column_name(subject.name)

                    value = row[value_column_name]
                    if value == '':
                        value = None

                    std = row.get(f"{value_column_name} STD", None)
                    if std == '':
                        std = None

                    measurement = Measurement(
                        study=study,
                        context=context,
                        timeInSeconds=time_in_seconds,
                        value=value,
                        std=std,
                    )
                    db_session.add(measurement)
                    measurements.append(measurement)

        db_session.add_all(measurements)
        db_session.commit()

        return measurements


# TODO (2025-05-15) Move or remove
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
