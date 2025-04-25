import time
from celery import shared_task
from celery.utils.log import get_task_logger

from db import get_session
from models import (
    CalculationTechnique,
    Calculation,
)

LOGGER = get_task_logger(__name__)


@shared_task
def update_calculations(calculation_technique_id, target_param_list):
    with get_session() as db_session:
        calculation_technique = db_session.get(CalculationTechnique, calculation_technique_id)
        LOGGER.info(f"Working on: {calculation_technique}")
        LOGGER.info(f"Target params: {target_param_list}")

        calculation_technique.state = 'in_progress'
        db_session.commit()

        try:
            calculation_technique.calculations = []
            for target_params in target_param_list:
                calculation = Calculation(
                    type=calculation_technique.type,
                    subjectId=target_params['subject_id'],
                    subjectType=target_params['subject_type'],
                    measurementTechniqueId=target_params['measurement_technique_id'],
                    calculationTechniqueId=calculation_technique.id,
                )
                db_session.add(calculation)
                calculation_technique.calculations.append(calculation)

            calculation_technique.state = 'ready'
            calculation_technique.error = None
            db_session.commit()
        except Exception as e:
            calculation_technique.state = 'error'
            calculation_technique.error = e
            db_session.commit()

            raise
