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
    aliased,
)
from sqlalchemy.ext.hybrid import hybrid_property

from models.orm_base import OrmBase
from models.bioreplicate import Bioreplicate
from models.strain import Strain
from models.metabolite import Metabolite
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

    @hybrid_property
    def timeInHours(self):
        return self.timeInSeconds // 3600

    def subject_join(subject_type):
        if subject_type == 'metabolite':
            name = Metabolite.metabo_name.label("subjectName")
            join = (Metabolite, Measurement.subjectId == Metabolite.chebi_id)
        elif subject_type == 'strain':
            name = Strain.memberName.label("subjectName")
            join = (Strain, Measurement.subjectId == Strain.strainId)
        elif subject_type == 'bioreplicate':
            name = Bioreplicate.bioreplicateId.label("subjectName")
            Subject = aliased(Bioreplicate)
            join = (Subject, Measurement.subjectId == Subject.bioreplicateUniqueId)

        return (name, join)

    @classmethod
    def insert_from_growth_csv(Self, db_session, study_id, csv_string):
        measurements = []
        reader = csv.DictReader(StringIO(csv_string), dialect='unix')

        techniques = []
        metabolites = {}

        for column in reader.fieldnames:
            if column in {'Position', 'Biological_Replicate_id', 'Time'}:
                continue
            elif column in {'FC', 'OD', 'pH'}:
                techniques.append(column)
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

            if bioreplicate_uuid is None:
                # Missing bioreplicate, skip
                continue

            # Global measurement from the FC/OD/pH column:
            for technique in techniques:
                value = row[technique]

                if row[technique] == '':
                    # Missing measurement:
                    value = None

                measurements.append(Self(
                    studyId=study_id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                    position=row['Position'],
                    timeInSeconds=round(float(row['Time']) * 3600),
                    pH=row.get('pH', None),
                    # TODO: units are not configurable
                    unit='Cells/mL',
                    technique=technique,
                    absoluteValue=value,
                    subjectType='bioreplicate',
                    subjectId=bioreplicate_uuid,
                ))

            for (name, chebi_id) in metabolites.items():
                value = row[name]

                if value == '':
                    # Missing measurement:
                    value = None

                measurements.append(Self(
                    position=row['Position'],
                    timeInSeconds=round(float(row['Time']) * 3600),
                    studyId=study_id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                    pH=row.get('pH', None),
                    # TODO: units are not configurable
                    unit='mM',
                    # TODO (2025-03-03) What is the actual technique?
                    technique='Metabolites',
                    absoluteValue=value,
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
                    ('counts', 'FC counts per species'),
                    ('Plate_counts', 'plates'),
                ]

                for measurement_type, technique in technique_mapping:
                    column_name = f"{strain_name}_{measurement_type}"
                    value = row.get(column_name, '')

                    if value == '':
                        # Missing measurement:
                        value = None

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
