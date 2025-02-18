import sqlalchemy as sql


class Strain:
    @staticmethod
    def find_for_experiment(db_conn, experiment_uuid, strain_name):
        params = {
            'strain_name': strain_name,
            'experiment_uuid': experiment_uuid,
        }
        strain_id = db_conn.execute(sql.text("""
            SELECT strainId
            FROM Strains
              INNER JOIN Experiments
                ON Experiments.experimentUniqueId = :experiment_uuid
              INNER JOIN Study
                ON Study.studyId = Experiments.studyId
            WHERE memberName = :strain_name
        """), params).scalar()

        return strain_id
