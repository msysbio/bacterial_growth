import tempfile
from datetime import datetime, UTC

from celery import shared_task
from celery.utils.log import get_task_logger

from db import FLASK_DB
from lib.r_script import RScript
from models import (
    ModelingRequest,
    ModelingResult,
)

LOGGER = get_task_logger(__name__)


@shared_task
def update_calculation_technique(modeling_request_id, target_param_list):
    db_session = FLASK_DB.session

    return _update_calculation_technique(db_session, modeling_request_id, target_param_list)


def _update_calculation_technique(db_session, modeling_request_id, target_param_list):
    modeling_request = db_session.get(ModelingRequest, modeling_request_id)
    modeling_request.state = 'in_progress'
    db_session.commit()

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        try:
            modeling_request.results = []

            for target_params in target_param_list:
                bioreplicate_uuid        = target_params['bioreplicate_uuid']
                subject_id               = target_params['subject_id']
                subject_type             = target_params['subject_type']
                measurement_technique_id = target_params['measurement_technique_id']

                measurement_technique = db_session.get_one(
                    ModelingResult,
                    measurement_technique_id,
                )

                modeling_result = ModelingResult(
                    type=modeling_request.type,
                    subjectId=subject_id,
                    subjectType=subject_type,
                    measurementTechniqueId=measurement_technique_id,
                    calculationTechniqueId=modeling_request.id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                )
                db_session.add(modeling_result)
                modeling_request.results.append(modeling_result)

                data = measurement_technique.get_subject_df(
                    db_session,
                    bioreplicate_uuid,
                    subject_id,
                    subject_type,
                )

                # If there is no standard deviation, remove it:
                if data['std'].isna().all():
                    data = data.drop(columns=['std'])

                # Remove rows with NA values
                data = data.dropna()

                rscript = RScript(root_path=tmp_dir_name)
                rscript.write_csv('input.csv', data)

                script_name = f"scripts/modeling/{modeling_request.type}.R"
                rscript.run(script_name, 'input.csv', 'coefficients.json')

                modeling_result.coefficients = rscript.read_json('coefficients.json')

                modeling_result.state = 'ready'
                modeling_result.calculatedAt = datetime.now(UTC)

            modeling_request.state = 'ready'
            modeling_request.error = None
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            modeling_request.state = 'error'

            # TODO (2025-04-28) Make "error" a text field, show it somewhere
            modeling_request.error = str(e)[0:100]
            db_session.commit()

            raise
