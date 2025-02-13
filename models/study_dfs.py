"""
A module with functions used to fetch data related to a study packaged up in
pandas dataframes.

This will likely be changed to be a bit more generally usable, since right now,
it's just bags of data that are rendered as tables.
"""

import sqlalchemy as sql
import pandas as pd


# TODO (2024-08-24) Sanitize: return (query, params)
def dynamical_query(all_advance_query):
    base_query = "SELECT DISTINCT studyId"
    search_final_query = ""

    for query_dict in all_advance_query:
        where_clause = ""
        if query_dict['option']:
            if query_dict['option'] == 'Project Name':
                project_name = query_dict['value'].lower()
                if project_name != '':
                    where_clause = f"""
                    FROM Study
                    WHERE projectUniqueID IN (
                        SELECT projectUniqueID
                        FROM Project
                        WHERE LOWER(projectName) LIKE '%{project_name}%'
                        )
                    """
            elif query_dict['option'] == 'Project ID':
                project_id = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE projectUniqueID IN (
                    SELECT projectUniqueID
                    FROM Project
                    WHERE projectId = '{project_id}'
                    )
                """
            elif query_dict['option'] == 'Study Name':
                study_name = query_dict['value'].lower()
                where_clause = f"""
                FROM Study
                WHERE LOWER(studyName) LIKE '%{study_name}%'
                """
            elif query_dict['option'] == 'Study ID':
                study_id = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE studyId = '{study_id}'
                """
            elif query_dict['option'] == 'Microbial Strain':
                microb_strain = query_dict['value'].lower()
                where_clause = f"""
                FROM Strains
                WHERE LOWER(memberName) LIKE '%{microb_strain}%'
                """
            elif query_dict['option'] == 'NCBI ID':
                microb_ID = query_dict['value']
                where_clause = f"""
                FROM Strains
                WHERE NCBId = '{microb_ID}'
                """
            elif query_dict['option'] == 'Metabolites':
                metabo = query_dict['value'].lower()
                where_clause = f"""
                FROM MetabolitePerExperiment
                WHERE LOWER(metabo_name) LIKE '%{metabo}%'
                """
            elif query_dict['option'] == 'chEBI ID':
                chebi_id = query_dict['value']
                where_clause = f"""
                FROM MetabolitePerExperiment
                WHERE chebi_id = '{chebi_id}'
                """
            elif query_dict['option'] == 'pH':
                start, end = query_dict['value']
                where_clause = f"""
                FROM Compartments
                WHERE initialPh BETWEEN {start} AND {end}
                """
        logic_add = ""
        if 'logic_operator' in query_dict:
            if query_dict['logic_operator'] == 'AND':
                logic_add = " AND studyId IN ("
            if query_dict['logic_operator'] == 'OR':
                logic_add = " OR studyId IN ("
            if query_dict['logic_operator'] == 'NOT':
                logic_add = " AND studyId NOT IN ("

        if logic_add != "":
            final_query = logic_add + " " + base_query + " " + where_clause + " )"
        else:
            final_query = base_query + " " + where_clause + " "

        search_final_query += final_query

    search_final_query = search_final_query + ";"
    return search_final_query


def get_general_info(studyId, conn):
    params = {'studyId': studyId}

    query = """
        SELECT studyId, studyName, studyDescription, studyURL, projectId
        FROM Study
        INNER JOIN Project
          ON Study.projectUniqueID = Project.projectUniqueID
        WHERE studyId = :studyId
        LIMIT 1
    """
    result = conn.execute(sql.text(query), params).one()._asdict()

    query = """
        SELECT memberName, strainId
        FROM Strains
        WHERE studyId = :studyId
        ORDER BY memberName ASC
    """
    result['members'] = list(conn.execute(sql.text(query), params).all())

    query = """
        SELECT DISTINCT technique
        FROM TechniquesPerExperiment
        WHERE studyId = :studyId
        ORDER BY technique ASC
    """
    result['techniques'] = list(conn.execute(sql.text(query), params).scalars())

    query = """
        SELECT DISTINCT metabo_name, chebi_id
        FROM MetabolitePerExperiment
        WHERE studyId = :studyId
        ORDER BY metabo_name ASC
    """
    result['metabolites'] = list(conn.execute(sql.text(query), params).all())

    return result


def get_experiments(studyId, conn):
    query = """
    SELECT
        E.experimentUniqueId,
        E.experimentId,
        E.experimentDescription,
        E.cultivationMode,
        GROUP_CONCAT(DISTINCT BRI.bioreplicateId) AS bioreplicateIds,
        E.controlDescription,
        GROUP_CONCAT(DISTINCT BR.bioreplicateId) AS control_bioreplicateIds,
        GROUP_CONCAT(DISTINCT C.communityId) AS communityIds,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM
        Experiments AS E
    LEFT JOIN
        BioReplicatesPerExperiment AS BRI ON E.experimentUniqueId = BRI.experimentUniqueId
    LEFT JOIN
        BioReplicatesPerExperiment AS BR ON E.experimentUniqueId = BR.experimentUniqueId
    LEFT JOIN
        Community AS C ON E.studyId = C.studyId
    LEFT JOIN
        CompartmentsPerExperiment AS CP ON E.experimentUniqueId = CP.experimentUniqueId
    WHERE
        E.studyId = %(studyId)s
        -- Note: Need to consider how to refer to controls while *uploading*,
        -- data spreadsheet breaks
        --
        -- AND BR.controls = 1
    GROUP BY
        E.experimentId,
        E.experimentUniqueId,
        E.experimentDescription,
        E.cultivationMode,
        E.controlDescription;
    """
    df_experiments = pd.read_sql(query, conn, params={'studyId': studyId})
    columns_to_exclude = ['experimentUniqueId']
    return df_experiments.drop(columns=columns_to_exclude)


def get_compartments(studyId, conn):
    query = "SELECT DISTINCT * FROM Compartments WHERE studyId = %(studyId)s;"
    df_compartments = pd.read_sql(query, conn, params={'studyId': studyId})
    columns_to_exclude = ['studyId', 'compartmentUniqueId']
    return df_compartments.drop(columns=columns_to_exclude)


def get_communities(studyId, conn):
    query = """
    SELECT
        C.communityId,
        GROUP_CONCAT(DISTINCT S.memberName) AS memberNames,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM
        Community AS C
    LEFT JOIN
        Strains AS S ON C.strainId = S.strainId
    LEFT JOIN
        CompartmentsPerExperiment AS CP ON CP.communityUniqueId = C.communityUniqueId
    WHERE
        C.studyId = %(studyId)s
    GROUP BY
        C.communityId;
    """
    df_communities = pd.read_sql(query, conn, params={'studyId': studyId})
    return df_communities


def get_microbial_strains(studyId, conn):
    query = "SELECT * FROM Strains WHERE studyId = %(studyId)s;"
    df_strains = pd.read_sql(query, conn, params={'studyId': studyId})
    columns_to_exclude = ['studyId']
    return df_strains.drop(columns=columns_to_exclude)


def get_biological_replicates(studyId, conn):
    query = """
    SELECT
        B.bioreplicateId,
        B.bioreplicateUniqueId,
        B.controls,
        B.OD,
        B.Plate_counts,
        B.pH,
        B.experimentId,
        BM.biosampleLink,
        BM.bioreplicateDescrition
    FROM
        BioReplicatesPerExperiment AS B
    LEFT JOIN
        BioReplicatesMetadata AS BM ON B.bioreplicateUniqueId = BM.bioreplicateUniqueId
    WHERE
        B.studyId = %(studyId)s;
        """
    df_bioreps = pd.read_sql(query, conn, params={'studyId': studyId})
    columns_to_exclude = ['bioreplicateUniqueId']
    return df_bioreps.drop(columns=columns_to_exclude)


def get_abundances(studyId, conn):
    query = """
    SELECT
        A.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        Abundances AS A
    JOIN
        Strains AS S ON A.strainId = S.strainId
    WHERE
        A.studyId = %(studyId)s;
        """
    df_abundances = pd.read_sql(query, conn, params={'studyId': studyId})
    return df_abundances


def get_fc_counts(studyId, conn):
    query = """
    SELECT
        F.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        FC_Counts AS F
    JOIN
        Strains AS S ON F.strainId = S.strainId
    WHERE
        F.studyId = %(studyId)s;
        """
    df_fc_counts = pd.read_sql(query, conn, params={'studyId': studyId})
    return df_fc_counts


def get_metabolites_per_replicate(studyId, conn):
    query = "SELECT * FROM MetabolitePerExperiment WHERE studyId = %(studyId)s;"
    df_metabolites = pd.read_sql(query, conn, params={'studyId': studyId})
    columns_to_exclude = ['experimentUniqueId', 'experimentId', 'bioreplicateUniqueId']
    return df_metabolites.drop(columns=columns_to_exclude)
