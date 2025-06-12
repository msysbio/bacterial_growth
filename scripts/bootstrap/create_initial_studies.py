from uuid import uuid4

from db import get_session
from app.model.lib.dev import bootstrap_study

STUDY_KEYS = [
    'synthetic_gut',
    'starvation_responses',
    'ri_bt_bh_in_chemostat_controls',
]

USER_UUID = str(uuid4())

with get_session() as db_session:
    for study_key in STUDY_KEYS:
        bootstrap_study(db_session, study_key, USER_UUID)

print(f"> Records created, owned by user with ID: {USER_UUID}")
