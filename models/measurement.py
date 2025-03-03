from io import StringIO
import csv
import enum
import functools
from decimal import Decimal

from sqlalchemy import (
    Enum,
    Integer,
    String,
    Numeric,
    ForeignKey,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)

from models.orm_base import OrmBase
from models.bioreplicate import Bioreplicate
from models.strain import Strain
from lib.db import execute_text


class Measurement(OrmBase):
    __tablename__ = "Measurements"

    class SubjectType(enum.Enum):
        metabolite   = 'metabolite'
        strain       = 'strain'
        bioreplicate = 'bioreplicate'

    id: Mapped[int] = mapped_column(primary_key=True)

    bioreplicateUniqueId: Mapped[int] = mapped_column(ForeignKey('BioReplicatesPerExperiment.bioreplicateUniqueId'))
    bioreplicate: Mapped['Bioreplicate'] = relationship(back_populates='measurements')

    # Note: should be a ForeignKey + relationship. However, ORM model is not
    # defined yet.
    studyId: Mapped[str] = mapped_column(String(100), nullable=False)

    position:      Mapped[str] = mapped_column(String(100), nullable=False)
    timeInSeconds: Mapped[int] = mapped_column(Integer,     nullable=False)
    pH:            Mapped[str] = mapped_column(String(100), nullable=False)
    unit:          Mapped[str] = mapped_column(String(100), nullable=False)

    # TODO (2025-02-13) Consider an enum
    technique: Mapped[str] = mapped_column(String(100), nullable=False)

    absoluteValue:    Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=True)
    absoluteValueStd: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=True)
    relativeValue:    Mapped[Decimal] = mapped_column(Numeric(10, 9), nullable=True)

    subjectType: Mapped[str] = mapped_column(Enum(SubjectType), nullable=False)
    subjectId:   Mapped[str] = mapped_column(String(100),       nullable=False)

    @classmethod
    def insert_from_growth_csv(Self, db_session, study_id, csv_string):
        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        technique = None
        metabolites = {}

        for column in reader.fieldnames:
            if column in {'Position', 'Biological_Replicate_id', 'Time', 'pH'}:
                continue
            elif column in {'FC', 'OD'}:
                technique = column
            else:
                # Metabolite, fetch chebi id
                # TODO (2025-02-18) Fetch them from MetaboliteForExperiment, get chebi_id through there
                chebi_id = execute_text(db_session, """
                    SELECT chebi_id
                    FROM Metabolites
                    WHERE metabo_name = :name
                """, name=column).scalar()
                metabolites[column] = chebi_id

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study_id, bioreplicate_id)

            if row[technique] == '':
                # Missing measurement, skip
                continue

            # Global measurement from the FC/OD column:
            measurements.append(Self(
                studyId=study_id,
                bioreplicateUniqueId=bioreplicate_uuid,
                position=row['Position'],
                timeInSeconds=round(float(row['Time']) * 3600),
                pH=row.get('pH', None),
                # TODO: units are not configurable
                unit='Cells/mL',
                technique=technique,
                absoluteValue=row[technique],
                subjectType='bioreplicate',
                subjectId=bioreplicate_uuid,
            ))

            for (name, chebi_id) in metabolites.items():
                if row[name] == '':
                    # Missing measurement, skip
                    continue

                measurements.append(Self(
                    position=row['Position'],
                    timeInSeconds=round(float(row['Time']) * 3600),
                    studyId=study_id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                    pH=row.get('pH', None),
                    # TODO: units are not configurable
                    unit='mM',
                    technique=technique,
                    absoluteValue=row[name],
                    subjectType='metabolite',
                    subjectId=chebi_id,
                ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements

    @classmethod
    def insert_from_reads_csv(Self, db_session, study_id, csv_string):
        measurements = []

        reader = csv.DictReader(StringIO(csv_string), dialect='unix')
        strains = {}

        strain_names = set()
        for suffix in ('_reads', '_counts', '_Plate_counts'):
            strain_names |= {c.removesuffix(suffix) for c in reader.fieldnames if c.endswith(suffix)}

        for strain_name in strain_names:
            strains[strain_name] = Strain.find_for_study(db_session, study_id, strain_name)

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, study_id, bioreplicate_id)

            for strain_name, strain_id in strains.items():
                technique_mapping = [
                    ('reads', '16S rRNA-seq'),
                    ('counts', 'FC per species'),
                    ('Plate_counts', 'plates'),
                ]

                for measurement_type, technique in technique_mapping:
                    column_name = f"{strain_name}_{measurement_type}"
                    value = row.get(column_name, '')

                    if value == '':
                        # Missing measurement, skip
                        continue

                    valueStd = row.get(f"{column_name}_std")
                    if valueStd == '':
                        valueStd = None

                    measurements.append(Self(
                        position=row['Position'],
                        timeInSeconds=round(float(row['Time']) * 3600),
                        studyId=study_id,
                        bioreplicateUniqueId=bioreplicate_uuid,
                        pH=row.get('pH', None),
                        # TODO: units are not configurable
                        unit='Cells/mL',
                        technique=technique,
                        absoluteValue=value,
                        absoluteValueStd=valueStd,
                        relativeValue=None,
                        subjectType='strain',
                        subjectId=strain_id,
                    ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements
