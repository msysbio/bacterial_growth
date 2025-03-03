from db import get_session
from pathlib import Path

import sqlalchemy as sql

from models.experiment import Experiment
from models.measurement import Measurement

with get_session() as db_session:
    for study_id in ['SMGDB00000001', 'SMGDB00000002', 'SMGDB00000003']:
        db_session.execute(sql.delete(Measurement).where(Measurement.studyId == study_id))

        growth_csv = Path(f'tmp_data/{study_id}/Growth_Metabolites.csv').read_text()
        Measurement.insert_from_growth_csv(db_session, study_id, growth_csv)

        reads_csv = Path(f'tmp_data/{study_id}/Sequencing_Reads.csv').read_text()
        Measurement.insert_from_reads_csv(db_session, study_id, reads_csv)

    db_session.commit()
