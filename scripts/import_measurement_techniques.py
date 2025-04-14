from db import get_session
from pathlib import Path

import sqlalchemy as sql

from models import (
    Study,
    MeasurementTechnique,
    Measurement,
)

with get_session() as db_session:
    for study_id in ['SMGDB00000001', 'SMGDB00000002', 'SMGDB00000003']:
        print(f"> Working on study: {study_id}")

        study = db_session.scalars(sql.select(Study).where(Study.studyId == study_id)).one()
        study_uuid = study.studyUniqueID

        db_session.execute(
            sql.delete(MeasurementTechnique)
            .where(MeasurementTechnique.studyUniqueID == study_uuid),
        )

        study_techniques = db_session.scalars(
            sql.select(Measurement.technique)
            .distinct()
            .where(Measurement.studyId == study_id)
        ).all()

        print(f"Techniques: {study_techniques}")

        (metabolite_ids, strain_ids) = (
            db_session.scalars(
                sql.select(Measurement.subjectId)
                .distinct()
                .where(
                    Measurement.studyId == study_id,
                    Measurement.subjectType == subjectType,
                )
            ).all()
            for subjectType in ('metabolite', 'strain')
        )

        for technique_name in study_techniques:
            if technique_name == 'pH':
                mt = MeasurementTechnique(
                    type='pH',
                    subjectType='bioreplicate',
                    units='',
                    studyUniqueID=study_uuid,
                )
            elif technique_name in ('OD', 'FC'):
                mt = MeasurementTechnique(
                    type=technique_name,
                    subjectType='bioreplicate',
                    units='Cells/mL',
                    studyUniqueID=study_uuid,
                )
            elif technique_name == 'FC counts per species':
                mt = MeasurementTechnique(
                    type='FC',
                    subjectType='strain',
                    units='Cells/mL',
                    studyUniqueID=study_uuid,
                    strainIds=strain_ids,
                )
            elif technique_name == '16S rRNA-seq':
                mt = MeasurementTechnique(
                    type='16s',
                    subjectType='strain',
                    units='Reads',
                    studyUniqueID=study_uuid,
                    strainIds=strain_ids,
                )
            elif technique_name == 'Metabolites':
                mt = MeasurementTechnique(
                    type='Metabolites',
                    subjectType='metabolite',
                    units='mM',
                    studyUniqueID=study_uuid,
                    metaboliteIds=metabolite_ids,
                )
            else:
                raise ValueError(f"Unexpected technique name: {technique_name}")

            db_session.add(mt)

            measurements = db_session.scalars(
                sql.select(Measurement)
                .where(Measurement.technique == technique_name)
            ).all()

            for measurement in measurements:
                measurement.techniqueId = mt.id
                db_session.add(measurement)

        db_session.commit()
