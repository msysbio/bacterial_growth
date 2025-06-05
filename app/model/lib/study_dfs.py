"""
A module with functions used to fetch data related to a study packaged up in
pandas dataframes.

This will likely be changed to be a bit more generally usable, since right now,
it's just bags of data that are rendered as tables.
"""

import sqlalchemy as sql


# TODO (2024-08-24) Sanitize: return (query, params)
def dynamical_query(all_advance_query):
    base_query = "SELECT DISTINCT studyId"
    search_final_query = ""

    for query_dict in all_advance_query:
        where_clause = ""
        if query_dict['option']:
            if query_dict['option'] == 'Project Name':
                project_name = query_dict['value'].strip().lower()
                if project_name != '':
                    where_clause = f"""
                    FROM Studies
                    WHERE projectUniqueID IN (
                        SELECT projectUniqueID
                        FROM Projects
                        WHERE LOWER(projectName) LIKE '%{project_name}%'
                    )
                    """
            elif query_dict['option'] == 'Project ID':
                project_id = query_dict['value']
                where_clause = f"""
                FROM Studies
                WHERE projectUniqueID IN (
                    SELECT projectUniqueID
                    FROM Projects
                    WHERE projectId = '{project_id}'
                )
                """
            elif query_dict['option'] == 'Study Name':
                study_name = query_dict['value'].strip().lower()
                where_clause = f"""
                    FROM Studies
                    WHERE LOWER(studyName) LIKE '%{study_name}%'
                """
            elif query_dict['option'] == 'Study ID':
                study_id = query_dict['value']
                where_clause = f"""
                FROM Studies
                WHERE studyId = '{study_id}'
                """
            elif query_dict['option'] == 'Microbial Strain':
                microb_strain = query_dict['value'].strip().lower()
                where_clause = f"""
                FROM Strains
                WHERE LOWER(name) LIKE '%{microb_strain}%'
                """
            elif query_dict['option'] == 'NCBI ID':
                microb_ID = query_dict['value']
                where_clause = f"""
                FROM Strains
                WHERE NCBId = '{microb_ID}'
                """
            elif query_dict['option'] == 'Metabolites':
                metabo = query_dict['value'].strip().lower()
                where_clause = f"""
                FROM StudyMetabolites
                WHERE LOWER(name) LIKE '%{metabo}%'
                """
            elif query_dict['option'] == 'chEBI ID':
                chebi_id = query_dict['value']
                where_clause = f"""
                FROM StudyMetabolites
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
