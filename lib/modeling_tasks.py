import tempfile
from datetime import datetime, UTC

import sqlalchemy as sql
from celery import shared_task
from celery.utils.log import get_task_logger

from db import FLASK_DB
from lib.r_script import RScript
from models import (
    ModelingRequest,
    ModelingResult,
    MeasurementContext,
)

LOGGER = get_task_logger(__name__)


@shared_task
def process_modeling_request(modeling_request_id, target_param_list):
    db_session = FLASK_DB.session

    return _process_modeling_request(db_session, modeling_request_id, target_param_list)


def _process_modeling_request(db_session, modeling_request_id, measurement_context_ids):
    modeling_request = db_session.get(ModelingRequest, modeling_request_id)
    modeling_request.state = 'in_progress'
    db_session.commit()

    measurement_contexts = db_session.scalars(
        sql.select(MeasurementContext)
        .where(MeasurementContext.id.in_(measurement_context_ids))
    ).all()

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        try:
            modeling_request.results = []

            for measurement_context in measurement_contexts:
                modeling_result = ModelingResult(
                    type=modeling_request.type,
                    request=modeling_request,
                    measurementContext=measurement_context,
                )
                db_session.add(modeling_result)
                modeling_request.results.append(modeling_result)

                data = measurement_context.get_df(db_session)

                # We don't need standard deviation for modeling:
                data = data.drop(columns=['std'])

                # Remove rows with NA values
                data = data.dropna()

                rscript = RScript(root_path=tmp_dir_name)
                rscript.write_csv('input.csv', data)

                script_name = f"scripts/modeling/{modeling_request.type}.R"
                rscript.run(script_name, 'input.csv', 'coefficients.json')

                # modeling_result.fit        = rscript.read_json('fit.json')
                modeling_result.coefficients = rscript.read_json('coefficients.json')

                modeling_result.state = 'ready'
                modeling_result.calculatedAt = datetime.now(UTC)

            modeling_request.state = 'ready'
            modeling_request.error = None
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            modeling_request.state = 'error'
            modeling_request.error = str(e)
            db_session.commit()

            raise
