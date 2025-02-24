import sqlalchemy as sql


def get_experiment(experimentId, conn):
    query = """
        SELECT
            E.experimentId,
            E.experimentDescription,
            GROUP_CONCAT(DISTINCT BRI.bioreplicateId) AS bioreplicateIds
        FROM
            Experiments AS E
        LEFT JOIN
            BioReplicatesPerExperiment AS BRI ON E.experimentUniqueId = BRI.experimentUniqueId
        WHERE
            E.experimentId = :experimentId
        GROUP BY
            E.experimentId,
            E.experimentDescription
    """
    return conn.execute(sql.text(query), {'experimentId': experimentId}).one()._asdict()
