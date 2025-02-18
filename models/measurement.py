from io import StringIO
import csv
import enum
import functools
from decimal import Decimal

from sqlalchemy import (
    Enum,
    ForeignKey,
    Integer,
    String,
    Numeric,
)
from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship,
)
import sqlalchemy as sql

from models.orm_base import OrmBase
from models.bioreplicate import Bioreplicate
from models.strain import Strain

class Measurement(OrmBase):
    __tablename__ = "Measurements"

    class SubjectType(enum.Enum):
        metabolite   = 'metabolite'
        strain       = 'strain'
        bioreplicate = 'bioreplicate'

    id: Mapped[int] = mapped_column(primary_key=True)

    # Note: should be a ForeignKey + relationship. However, ORM model is not
    # defined yet.
    bioreplicateUniqueId: Mapped[int] = mapped_column(Integer, nullable=False)

    position:      Mapped[str] = mapped_column(String(100), nullable=False)
    timeInSeconds: Mapped[int] = mapped_column(Integer,     nullable=False)
    pH:            Mapped[str] = mapped_column(String(100), nullable=False)
    unit:          Mapped[str] = mapped_column(String(100), nullable=False)

    # TODO (2025-02-13) Consider an enum
    technique: Mapped[str] = mapped_column(String(100), nullable=False)

    absoluteValue: Mapped[Decimal] = mapped_column(Numeric(20, 2), nullable=True)
    relativeValue: Mapped[Decimal] = mapped_column(Numeric(10, 9), nullable=True)

    subjectType: Mapped[str] = mapped_column(Enum(SubjectType), nullable=False)
    subjectId:   Mapped[str] = mapped_column(String(100),       nullable=False)

    @classmethod
    def insert_from_growth_csv(cls, db_session, experiment_uuid, csv_string):
        measurements = []
        bioreplicate_uuids = {}

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
                chebi_id = db_session.execute(sql.text("""
                    SELECT chebi_id
                    FROM Metabolites
                    WHERE metabo_name = :name
                """), {'name': column}).scalar()
                metabolites[column] = chebi_id

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_experiment)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, experiment_uuid, bioreplicate_id)

            # Global measurement from the FC/OD column:
            measurements.append(Measurement(
                position=row['Position'],
                timeInSeconds=float(row['Time']),
                bioreplicateUniqueId=bioreplicate_uuid,
                pH=row.get('pH', None),
                # TODO: units are not configurable
                unit='Cells/mL',
                technique=technique,
                absoluteValue=row[technique],
                relativeValue=None,
                subjectType='bioreplicate',
                subjectId=bioreplicate_uuid,
            ))

            for (name, chebi_id) in metabolites.items():
                # TODO (2025-02-17) Relative or absolute based on OD/FC?

                measurements.append(cls(
                    position=row['Position'],
                    timeInSeconds=float(row['Time']),
                    bioreplicateUniqueId=bioreplicate_uuid,
                    pH=row.get('pH', None),
                    # TODO: units are not configurable
                    unit='mM',
                    technique=technique,
                    absoluteValue=row[name],
                    relativeValue=None,
                    subjectType='metabolite',
                    subjectId=chebi_id,
                ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements

    @classmethod
    def insert_from_reads_csv(cls, db_session, experiment_uuid, csv_string):
        measurements = []

        reader = csv.DictReader(StringIO(csv_string), dialect='unix')
        strains = {}

        strain_names = { c.removesuffix('_reads') for c in reader.fieldnames if c.endswith('_reads') }
        strain_names |= { c.removesuffix('_counts') for c in reader.fieldnames if c.endswith('_counts') }

        for strain_name in strain_names:
            strains[strain_name] = Strain.find_for_experiment(db_session, experiment_uuid, strain_name)

        find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_experiment)

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']
            bioreplicate_uuid = find_bioreplicate_uuid(db_session, experiment_uuid, bioreplicate_id)

            for strain_name, strain_id in strains.items():
                for measurement_type in ("reads", "counts"):
                    column_name = f"{strain_name}_{measurement_type}"

                    if measurement_type == 'reads':
                        technique = '16S rRNA-seq'
                    elif measurement_type == 'counts':
                        # TODO (2025-02-18) What can "counts" be here?
                        technique = 'plates'

                    measurements.append(cls(
                        position=row['Position'],
                        timeInSeconds=float(row['Time']),
                        bioreplicateUniqueId=bioreplicate_uuid,
                        pH=row.get('pH', None),
                        # TODO: units are not configurable
                        unit='Cells/mL',
                        technique=technique,
                        absoluteValue=row[column_name],
                        relativeValue=None,
                        subjectType='strain',
                        subjectId=strain_id,
                    ))

        db_session.add_all(measurements)
        db_session.commit()

        return measurements
