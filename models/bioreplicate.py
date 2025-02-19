from lib.db import execute_text


class Bioreplicate:
    @staticmethod
    def find_for_study(db_conn, study_id, bioreplicate_id):
        return execute_text(db_conn, """
            SELECT bioreplicateUniqueId
            FROM BioReplicatesPerExperiment
            WHERE studyId = :study_id
              AND bioreplicateId = :bioreplicate_id
        """, study_id=study_id, bioreplicate_id=bioreplicate_id).scalar()
