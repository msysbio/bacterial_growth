import time
import tempfile
from datetime import datetime, UTC

from celery import shared_task
from celery.utils.log import get_task_logger

from db import FLASK_DB
from lib.r_script import RScript
from models import (
    CalculationTechnique,
    Calculation,
    MeasurementTechnique,
)

LOGGER = get_task_logger(__name__)


@shared_task
def update_calculation_technique(calculation_technique_id, target_param_list):
    db_session = FLASK_DB.session

    return _update_calculation_technique(db_session, calculation_technique_id, target_param_list)


def _update_calculation_technique(db_session, calculation_technique_id, target_param_list):
    calculation_technique = db_session.get(CalculationTechnique, calculation_technique_id)
    calculation_technique.state = 'in_progress'
    db_session.commit()

    with tempfile.TemporaryDirectory() as tmp_dir_name:
        try:
            calculation_technique.calculations = []
            for target_params in target_param_list:
                bioreplicate_uuid        = target_params['bioreplicate_uuid']
                subject_id               = target_params['subject_id']
                subject_type             = target_params['subject_type']
                measurement_technique_id = target_params['measurement_technique_id']

                measurement_technique = db_session.get_one(
                    MeasurementTechnique,
                    measurement_technique_id,
                )

                calculation = Calculation(
                    type=calculation_technique.type,
                    subjectId=subject_id,
                    subjectType=subject_type,
                    measurementTechniqueId=measurement_technique_id,
                    calculationTechniqueId=calculation_technique.id,
                    bioreplicateUniqueId=bioreplicate_uuid,
                )
                db_session.add(calculation)
                calculation_technique.calculations.append(calculation)

                data = measurement_technique.get_subject_df(
                    db_session,
                    bioreplicate_uuid,
                    subject_id,
                    subject_type,
                )

                rscript = RScript(root_path=tmp_dir_name)
                rscript.write_csv('input.csv', data)
                output = rscript.run('scripts/modeling/baranyi_roberts.R', 'input.csv', 'coefficients.json')
                calculation.coefficients = rscript.read_json('coefficients.json')
                calculation.state = 'ready'
                calculation.calculatedAt = datetime.now(UTC)

            calculation_technique.state = 'ready'
            calculation_technique.error = None
            db_session.commit()
        except Exception as e:
            db_session.rollback()
            calculation_technique.state = 'error'
            calculation_technique.error = str(e)[0:100]
            db_session.commit()

            raise
