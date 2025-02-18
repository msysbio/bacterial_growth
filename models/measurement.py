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
        csv_io = StringIO(csv_string)
        measurements = []
        bioreplicate_uuids = {}

        reader = csv.DictReader(csv_io, dialect='unix')

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

                measurements.append(Measurement(
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
