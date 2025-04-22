import csv
import functools
from io import StringIO
from pathlib import Path

import sqlalchemy as sql

from db import get_session
from lib.db import execute_text
from models import (
    Measurement,
    Bioreplicate,
    Strain,
)

# Note: insert methods taken from Measurement, work on legacy-format data

def insert_from_growth_csv(db_session, study_id, csv_string):
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

            # TODO: units need to be configurable
            if technique == 'pH':
                unit = None
            else:
                unit = 'Cells/mL'

            measurements.append(Measurement(
                studyId=study_id,
                bioreplicateUniqueId=bioreplicate_uuid,
                position=row['Position'],
                timeInSeconds=round(float(row['Time']) * 3600),
                pH=row.get('pH', None),
                unit=unit,
                technique=technique,
                value=value,
                subjectType='bioreplicate',
                subjectId=bioreplicate_uuid,
            ))

        for (name, chebi_id) in metabolites.items():
            value = row[name]

            if value == '':
                # Missing measurement:
                value = None

            measurements.append(Measurement(
                studyId=study_id,
                bioreplicateUniqueId=bioreplicate_uuid,
                position=row['Position'],
                timeInSeconds=round(float(row['Time']) * 3600),
                pH=row.get('pH', None),
                # TODO: units are not configurable
                unit='mM',
                # TODO (2025-03-03) What is the actual technique?
                technique='Metabolites',
                value=value,
                subjectType='metabolite',
                subjectId=chebi_id,
            ))

    db_session.add_all(measurements)
    db_session.commit()

    return measurements

def insert_from_reads_csv(db_session, study_id, csv_string):
    measurements = []

    reader = csv.DictReader(StringIO(csv_string), dialect='unix')
    strains = {}

    technique_mapping = {
        'reads': '16S rRNA-seq',
        'counts': 'FC counts per species',
        'Plate_counts': 'plates',
    }
    available_technique_mapping = {}

    strain_names = set()
    for suffix in ('reads', 'counts', 'Plate_counts'):
        for c in reader.fieldnames:
            if c.endswith(f'_{suffix}'):
                strain_names.add(c.removesuffix(f'_{suffix}'))
                available_technique_mapping[suffix] = technique_mapping[suffix]

    for strain_name in strain_names:
        strains[strain_name] = Strain.find_for_study(db_session, study_id, strain_name)

    find_bioreplicate_uuid = functools.cache(Bioreplicate.find_for_study)

    for row in reader:
        bioreplicate_id = row['Biological_Replicate_id']
        bioreplicate_uuid = find_bioreplicate_uuid(db_session, study_id, bioreplicate_id)

        if bioreplicate_uuid is None:
            print(f"Missing bioreplicate for {study_id}: {bioreplicate_id}")
            # Missing bioreplicate, skip
            continue

        for strain_name, strain_id in strains.items():
            for measurement_type, technique in available_technique_mapping.items():
                column_name = f"{strain_name}_{measurement_type}"
                value = row.get(column_name, '')

                # TODO (2025-03-05) Class that translates spreadsheet terminology to code terminology (reads, std, etc)

                if value == '':
                    # Missing measurement:
                    value = None

                valueStd = row.get(f"{column_name}_std")
                if valueStd == '':
                    valueStd = None

                measurements.append(Measurement(
                    position=row['Position'],
                    timeInSeconds=round(float(row['Time']) * 3600),
                    studyId=study_id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                    pH=row.get('pH', None),
                    # TODO: units are not configurable
                    unit='Cells/mL',
                    technique=technique,
                    value=value,
                    std=valueStd,
                    subjectType='strain',
                    subjectId=strain_id,
                ))

    db_session.add_all(measurements)
    db_session.commit()

    return measurements

with get_session() as db_session:
    for study_id in ['SMGDB00000001', 'SMGDB00000002', 'SMGDB00000003']:
        db_session.execute(sql.delete(Measurement).where(Measurement.studyId == study_id))

        growth_csv = Path(f'tmp_data/{study_id}/Growth_Metabolites.csv').read_text()
        insert_from_growth_csv(db_session, study_id, growth_csv)

        reads_csv = Path(f'tmp_data/{study_id}/Sequencing_Reads.csv').read_text()
        insert_from_reads_csv(db_session, study_id, reads_csv)

    db_session.commit()
