import sqlalchemy as sql


class Bioreplicate:
    @staticmethod
    def find_for_experiment(db_conn, experiment_uuid, bioreplicate_id):
        params = {
            'bioreplicate_id': bioreplicate_id,
            'experiment_uuid': experiment_uuid,
        }
        bioreplicate_uuid = db_conn.execute(sql.text("""
            SELECT bioreplicateUniqueId
            FROM BioReplicatesPerExperiment
            WHERE bioreplicateId = :bioreplicate_id
            AND experimentUniqueId = :experiment_uuid
        """), params).scalar()

        return bioreplicate_uuid
