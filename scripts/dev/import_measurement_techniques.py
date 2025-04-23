from db import get_session
from pathlib import Path

import sqlalchemy as sql

from models import (
    Study,
    MeasurementTechnique,
    Measurement,
)

with get_session() as db_session:
    for study_id in ['SMGDB00000001', 'SMGDB00000002']:
        print(f"> Working on study: {study_id}")

        study = db_session.scalars(sql.select(Study).where(Study.studyId == study_id)).one()
        study_uuid = study.studyUniqueID

        db_session.execute(
            sql.delete(MeasurementTechnique)
            .where(MeasurementTechnique.studyUniqueID == study_uuid),
        )

        measurements = db_session.scalars(
            sql.select(Measurement)
            .where(Measurement.studyId == study_id)
        ).all()

        technique_names = {m.technique for m in measurements}

        print(f"Techniques: {technique_names}")

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

        for technique_name in technique_names:
            if technique_name == 'pH':
                mt = MeasurementTechnique(
                    type='ph',
                    subjectType='bioreplicate',
                    units='',
                    studyUniqueID=study_uuid,
                )
            elif technique_name in ('OD', 'FC'):
                mt = MeasurementTechnique(
                    type=technique_name.lower(),
                    subjectType='bioreplicate',
                    units='Cells/mL',
                    studyUniqueID=study_uuid,
                )
            elif technique_name == 'FC counts per species':
                mt = MeasurementTechnique(
                    type='fc',
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
                    type='metabolite',
                    subjectType='metabolite',
                    units='mM',
                    studyUniqueID=study_uuid,
                    metaboliteIds=metabolite_ids,
                )
            else:
                raise ValueError(f"Unexpected technique name: {technique_name}")

            db_session.add(mt)
            for m in measurements:
                if m.technique == technique_name:
                    m.techniqueRecord = mt
                    db_session.add(m)


        db_session.commit()
