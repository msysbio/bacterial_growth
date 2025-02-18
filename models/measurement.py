from io import StringIO
import csv
import enum
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

        for row in reader:
            bioreplicate_id = row['Biological_Replicate_id']

            if (experiment_uuid, bioreplicate_id) not in bioreplicate_uuids:
                # Fetch unique id corresponding to this bioreplicate in this experiment:
                params = {
                    'bioreplicate_id': bioreplicate_id,
                    'experiment_uuid': experiment_uuid,
                }
                bioreplicate_uuid = db_session.execute(sql.text("""
                    SELECT bioreplicateUniqueId
                    FROM BioReplicatesPerExperiment
                    WHERE bioreplicateId = :bioreplicate_id
                    AND experimentUniqueId = :experiment_uuid
                """), params).scalar()
                bioreplicate_uuids[(experiment_uuid, bioreplicate_id)] = bioreplicate_uuid

            # TODO (2025-02-18) Add measurements for all cells

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
