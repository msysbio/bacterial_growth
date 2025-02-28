import sqlalchemy as sql
from sqlalchemy.dialects import mysql
import pandas as pd

from db import get_connection
from models.measurement import Measurement
from models.metabolite import Metabolite
from models.strain import Strain
from models.bioreplicate import Bioreplicate

class MeasurementChart():
    def __init__(self, study_id, experiment_uuid):
        self.study_id          = study_id
        self.experiment_uuid   = experiment_uuid

    def get_single_df(self, bioreplicate_uuids, *, technique, subject_type):
        if subject_type == 'metabolite':
            subjectName = Metabolite.metabo_name.label("subjectName")
            subjectJoin = (Metabolite, Measurement.subjectId == Metabolite.chebi_id)
        elif subject_type == 'strain':
            subjectName = Strain.memberName.label("subjectName")
            subjectJoin = (Strain, Measurement.subjectId == Strain.strainId)

        query = (
            sql.select(
                (Measurement.timeInSeconds // 3600).label("time"),
                Measurement.absoluteValue.label("value"),
                subjectName,
            )
            .join(*subjectJoin)
            .where(
                Bioreplicate.bioreplicateUniqueId.in_(bioreplicate_uuids),
                Measurement.technique == technique,
                Measurement.subjectType == subject_type,
            )
            .order_by('subjectName', Measurement.timeInSeconds)
        )
        statement = query.compile(dialect=mysql.dialect())

        with get_connection() as db_conn:
            return pd.read_sql(statement, db_conn)
