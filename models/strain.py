from lib.db import execute_text


class Strain:
    @staticmethod
    def find_for_study(db_conn, study_id, strain_name):
        return execute_text(db_conn, """
            SELECT strainId
            FROM Strains
            WHERE studyId = :study_id
              AND memberName = :strain_name
        """, study_id=study_id, strain_name=strain_name).scalar()
