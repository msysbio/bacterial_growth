import sqlalchemy as sql

from db import get_transaction

to_be_deleted = [
    ('SMGDB00000004', '36d5f4fa-0d72-4669-a6ba-ddd0608ebc65'),
    ('SMGDB00000005', '0107a905-5536-4b34-b69c-9c3aca9a3092'),
    ('SMGDB00000006', '819b1af3-da4e-443c-ba9d-fdc9866b56d8'),
]

with get_transaction() as conn:
    for study_id, study_uuid in to_be_deleted:
        # Clear out previous data by studyId, in reverse insertion order:
        data_tables = [
            "Measurements",
            "MetabolitePerExperiment",
            "Bioreplicates",
            "TechniquesPerExperiment",
            "CompartmentsPerExperiment",
            "Perturbation",
            "Community",
            "Experiments",
            "Compartments",
            "Strains",
        ]

        for table in data_tables:
            conn.execute(
                sql.text(f"DELETE FROM {table} WHERE studyId = :study_id"),
                {'study_id': study_id}
            )

        # Clear out previous data by studyUniqueID, in reverse insertion order:
        data_tables = [
            "MeasurementTechniques",
        ]
        for table in data_tables:
            conn.execute(
                sql.text(f"DELETE FROM {table} WHERE studyUniqueID = :study_uuid"),
                {'study_uuid': study_uuid}
            )

        conn.execute(
            sql.text(f"DELETE FROM Study WHERE studyUniqueID = :study_uuid"),
            {'study_uuid': study_uuid}
        )
