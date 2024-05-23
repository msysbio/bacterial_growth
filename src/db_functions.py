import os
import mysql.connector
import warnings
import streamlit as st
import sys
filepath = os.path.realpath(__file__)
current_dir = os.path.dirname(filepath)
sys.path.append(current_dir)
from constants import *


def execute(phrase):
    """
    This function create a connection to the database and execute a command.

    :param phrase: str SQL sentence to execute
    :return: list of str received from the database
    """
    try:
        cnx = mysql.connector.connect(user=USER, password=PASSWORD, host=HOST, port=PORT,database=DATABASE)
        cursor = cnx.cursor()
        cursor.execute(phrase)
        res = []
        for row in cursor:
            res.append(row)
        # Fetch and handle warnings
        warnings = cursor.fetchwarnings()
        if warnings:
            for warning in warnings:
                print("\t\t ** Warning - ", warning)

        cursor.close()
        cnx.commit()
        cnx.close()
        return res
    except mysql.connector.Error as err:
        print("\nSomething went wrong: {}".format(err),'\n')
        exit()



def addRecord(table, args):
    """
    Add new entry into the db

    :param table: table of the DB
    :param args: dictionary with the data to insert (key = db field name. value = insert value)
    :return: id of the inserted record
    """
    # Insert into table
    fields, values = getInsertFieldsValues(args)
    # return fields, values
    phrase = "INSERT IGNORE INTO " +table+" "+fields+" VALUES "+values
    print(phrase)
    # return phrase
    res = execute(phrase)
    print(res)
    return res

    # Get the name of the primary key field
    phrase = "SHOW KEYS FROM "+table+" WHERE Key_name = 'PRIMARY'"
    res = execute(phrase)
    print(res)
    pk = res[0][4]
    print(pk)

    # Get the value of the primary key (this will return the value both if it was inserted or ignored)
    where_clause = getWhereClause(args)
    print(where_clause)
    phrase = "SELECT "+pk+" FROM "+table+" "+where_clause
    res = execute(phrase)
    print(res)
    if not res:
        last_id = 'WARNING'
    else:
        last_id = res[0][0]

    return last_id

def countRecords(table, args):
    '''
    Count the records in one table for specific args

    :param table
    :param args: dictionary with the data to find and count (key = db field name. value = insert value)
    :return count int
    '''
    phrase = "SELECT COUNT(*) FROM " + table
    if args:
        where_clause = getWhereClause(args)
        phrase = phrase+" "+where_clause
    res = execute(phrase)
    return res[0][0]

def getAllRecords(table, args):
    '''
    Return all the records in one table for specific args

    :param table
    :param args: dictionary with the data to return (key = db field name. value = insert value)
    :return list of records
    '''
    phrase = "SELECT * FROM " + table
    if args:
        where_clause = getWhereClause(args)
        phrase = phrase+" "+where_clause
    res = execute(phrase)
    return res

def getChebiId(metabolite):

    phrase = f"SELECT cheb_id FROM Metabolites WHERE metabo_name = '{metabolite}' ;"
    res = execute(phrase)
    print(res)
    return res[0][0]

def getFiles(fields, args):
    where_clause = getWhereClause(args)
    fields_clause = getSelectFields(fields)

    phrase = "SELECT "+fields_clause+" FROM TechnicalReplicate "+where_clause
    res = execute(phrase)
    return res

def getRecords(table, fields, args):
    where_clause = getWhereClause(args)
    fields_clause = getSelectFields(fields)

    phrase = "SELECT "+fields_clause+" FROM "+table+" "+where_clause
    res = execute(phrase)
    return res

def getMetaboliteID(metabolite):
    phrase = f"SELECT Metabolites.cheb_id, Metabolites.metabo_name FROM Metabolites WHERE Metabolites.metabo_name = '{metabolite}';"
    res = execute(phrase)
    if not res:
        phrase = "SELECT Metabolites.cheb_id, Metabolites.metabo_name FROM Metabolites JOIN MetaboliteSynonym ON Metabolites.cheb_id = MetaboliteSynonym.cheb_id "
        where = f"WHERE MetaboliteSynonym.synonym_value = '{metabolite}';"
        query= phrase +where
        res = execute(query)
    return res

# DATABASE SUPPLEMENTARY FUNCTIONS
# =================================

def getInsertFieldsValues(args):
    '''
    Create the fields and values strings to be inserted in the db

    :param args: dictionary with the data to return (key = db field name. value = insert value)
    :return str with part of query
    '''
    fields = "("
    values = "("
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    return [fields, values]

def getSelectFields(args):
    '''
    Create the str with the fields to be returned from db

    :args list or dictionary with fields to look for
    :return str clause
    '''
    clause = ""
    for field in args:
        clause = clause + field + ", "
    clause = clause[:-2]
    return clause

def getWhereClause(args):
    '''
    Create the str with the where clause

    :args dictionary with the data to return (key = db field name. value = insert value)
    :return str clause
    '''
    if len(args) == 0:
        clause = ''
    else:
        clause = "WHERE ("
        for key, val in args.items():
            if val == 'null':
                clause = clause + key + " IS NULL AND "
            elif val == 'not null':
                clause = clause + key + " IS NOT NULL AND "
            else:
                clause = clause + key + "= '" + str(val) + "' AND "

        clause = clause[:-5] + ')'

    return clause

def getWhereInClause(args):
    '''
    Create the str with the where clause when it must contain and IN operator

    :args dictionary with the data to return (key = db field name. value = insert value)
    :return str clause
    '''
    if len(args) == 0:
        clause = ''
    else:
        clause = "WHERE ("
        for key, val in args.items():
            if key == 'bacteriaSpecies':
                val = str(val).replace(",)",")")
                clause = clause + key +" IN "+ str(val) + " AND "
            elif val == 'null':
                clause = clause + key + " IS NULL AND "
            elif val == 'not null':
                clause = clause + key + " IS NOT NULL AND "
            else:
                clause = clause + key + "= '" + str(val) + "' AND "

        clause = clause[:-5] + ')'

    return clause


def getJoinClause(table_from, table_to, field):
    '''
    Create the str with the join clause

    :param table_from and table_to: tables to be joined
    :param field: common field
    :return str clause
    '''
    clause = "JOIN "+table_to+" ON "+table_to+"."+field+" = "+table_from+"."+field
    return clause

def getGroupByClause(field):
    '''
    Get the str with the group by clause

    :param field
    :return str clause
    '''
    clause = "GROUP BY " + field
    return clause

def getHavingClause(agg_function, field, operator, quant, distinct=False):
    '''
    Get the str with the having clause

    :param agg_function: MIN(), MAX(), SUM(), AVG() or COUNT()
    :param field
    :param operator and quant: to build up the having condition. i.e. having id > 5
    :param distint: boolean if distinct must be added
    :return str clause
    '''
    clause = "HAVING "+agg_function
    if distinct == False:
        clause = clause + "("+field+") "+operator+" "+str(quant)
    elif distinct == True:
        clause = clause +"(DISTINCT "+field+") "+operator+" "+str(quant)
    return clause

def getGeneralInfo(studyID, conn):
    query = f"SELECT * FROM Study WHERE studyId = '{studyID}';"
    df_general = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId','projectUniqueID','studyUniqueID']
    df_general.drop(columns_to_exclude, axis=1)
    query = f"SELECT CONCAT(memberName, ' (', NCBId, ')') AS transformed_output FROM Strains WHERE studyId = '{studyID}';"
    micro_strains = conn.query(query, ttl=600)
    df_general['memberName'] = ', '.join(micro_strains['transformed_output'])
    query = f"SELECT DISTINCT technique FROM TechniquesPerExperiment WHERE studyId = '{studyID}';"
    techniques = conn.query(query, ttl=600)
    df_general['techniques'] = ', '.join(techniques['technique'])
    query = f"SELECT DISTINCT CONCAT(metabo_name, ' (', cheb_id, ')') AS transformed_output FROM MetabolitePerExperiment WHERE studyId = '{studyID}';"
    metabolites = conn.query(query, ttl=600)
    df_general['metabolites'] = ', '.join(metabolites['transformed_output'])

    return df_general.drop(columns=columns_to_exclude)


## New functions t build tables in the interface getting data from the db

def getExperiments(studyID, conn):
    query = f"""
    SELECT
        E.experimentUniqueId,
        E.experimentId,
        E.experimentDescription,
        E.cultivationMode,
        GROUP_CONCAT(DISTINCT BRI.bioreplicateId) AS bioreplicateIds,
        E.controlDescription,
        GROUP_CONCAT(DISTINCT BR.bioreplicateId) AS control_bioreplicateIds,
        GROUP_CONCAT(DISTINCT C.comunityId) AS comunityIds,
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
        E.studyId = '{studyID}'
        AND BR.controls = 1
    GROUP BY
        E.experimentId,
        E.experimentUniqueId,
        E.experimentDescription,
        E.cultivationMode,
        E.controlDescription;
    """
    df_experiments = conn.query(query, ttl=600)
    columns_to_exclude = ['experimentUniqueId']
    return df_experiments.drop(columns=columns_to_exclude)

def getMicrobialStrains(studyID, conn):
    query = f"SELECT * FROM Strains WHERE studyId = '{studyID}';"
    df_Bacteria = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId']
    return df_Bacteria.drop(columns=columns_to_exclude)

def getCompartment(studyID, conn):
    query = f"SELECT DISTINCT * FROM Compartments WHERE studyId = '{studyID}';"
    df_Compartment = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId','compartmentUniqueId']
    return df_Compartment.drop(columns=columns_to_exclude)

def getMetabolite(studyID, conn):
    query = f"SELECT * FROM MetabolitePerExperiment  WHERE studyId = '{studyID}';"
    df_Metabolite = conn.query(query, ttl=600)
    columns_to_exclude = ['experimentUniqueId','experimentId','bioreplicateUniqueId']
    return df_Metabolite.drop(columns=columns_to_exclude)

def getPerturbations(studyID, conn):
    query = f"SELECT * FROM Perturbation WHERE studyId = '{studyID}';"
    df_perturbations = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId', 'perturbationUniqueid']
    return df_perturbations.drop(columns=columns_to_exclude)

def getCommunities(studyID, conn):
    query = f"""
    SELECT
        C.comunityId,
        GROUP_CONCAT(DISTINCT S.memberName) AS memberNames,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM
        Community AS C
    LEFT JOIN
        Strains AS S ON C.strainId = S.strainId
    LEFT JOIN
        CompartmentsPerExperiment AS CP ON CP.comunityUniqueId = C.comunityUniqueId
    WHERE
        C.studyId = '{studyID}'
    GROUP BY
        C.comunityId;
    """
    df_communities = conn.query(query, ttl=600)
    #columns_to_exclude = ['studyId', 'perturbationUniqueId']
    return df_communities

def getBiorep(studyID, conn):
    query = f"""
    SELECT
        B.bioreplicateId,
        B.bioreplicateUniqueId,
        B.controls,
        B.OD,
        B.Plate_counts,
        B.pH,
        BM.biosampleLink,
        BM.bioreplicateDescrition
    FROM
        BioReplicatesPerExperiment AS B
    LEFT JOIN
        BioReplicatesMetadata AS BM ON B.bioreplicateUniqueId = BM.bioreplicateUniqueId
    WHERE
        B.studyId = '{studyID}';
        """
    df_bioreps = conn.query(query, ttl=600)
    columns_to_exclude = ['bioreplicateUniqueId']
    return df_bioreps.drop(columns=columns_to_exclude)

def getAbundance(studyID, conn):
    query = f"""
    SELECT
        A.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        Abundances AS A
    JOIN
        Strains AS S ON A.strainId = S.strainId
    WHERE
        A.studyId = '{studyID}';
        """
    df_abundances = conn.query(query, ttl=600)
    return df_abundances

def getFC(studyID, conn):
    query = f"""
    SELECT
        F.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        FC_Counts AS F
    JOIN
        Strains AS S ON F.strainId = S.strainId
    WHERE
        F.studyId = '{studyID}';
        """
    df_FC = conn.query(query, ttl=600)
    return df_FC

def getPrivateProjectID(private_project_id, conn):
    query = f"""
    SELECT
        *
    FROM
        Study
    WHERE
        projectUniqueID = '{private_project_id}';
        """
    df_proyect = conn.query(query, ttl=600)
    return df_proyect

def getProjectInfo(private_project_id, conn):
    query = f"""
    SELECT
        *
    FROM
        Project
    WHERE
        projectUniqueID = '{private_project_id}';
        """
    df_proyect = conn.query(query, ttl=600)
    return df_proyect

def getProjectID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Project;"
    number_projects = conn.query(query, ttl=600)
    next_number = int(number_projects.iloc[0].iloc[0]) + 1
    Project_ID = "PMGDB{:06d}".format(next_number)
    return Project_ID

def getStudyID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Study;"
    number_projects = conn.query(query, ttl=600)
    next_number = int(number_projects.iloc[0].iloc[0]) + 1
    Study_ID = "SMGDB{:08d}".format(next_number)
    return Study_ID

def dynamical_query(all_advance_query):
    base_query = "SELECT DISTINCT studyId"
    search_final_query =  ""
    for query_dict in all_advance_query:
        where_clause = ""
        if query_dict['option']:
            if query_dict['option'] == 'Project Name':
                project_name = query_dict['value']
                if project_name !=  '':
                    where_clause = f"""
                    FROM Study
                    WHERE projectUniqueID IN (
                        SELECT projectUniqueID
                        FROM Project
                        WHERE projectName LIKE '%{project_name}%'
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
                study_name = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE studyName LIKE '%{study_name}%'
                """
            elif query_dict['option'] == 'Study ID':
                study_id = query_dict['value']
                where_clause = f"""
                FROM Study
                WHERE studyId = '{study_id}'
                """
            elif query_dict['option'] == 'Microbial Strain':
                microb_strain = query_dict['value']
                where_clause = f"""
                FROM Strains
                WHERE memberName LIKE '%{microb_strain}%'
                """
            elif query_dict['option'] == 'NCBI ID':
                microb_ID = query_dict['value']
                where_clause = f"""
                FROM Strains
                WHERE NCBId = '{microb_ID}'
                """
            elif query_dict['option'] == 'Metabolites':
                metabo = query_dict['value']
                where_clause = f"""
                FROM MetabolitePerExperiment
                WHERE metabo_name LIKE '%{metabo}%'
                """
            elif query_dict['option'] == 'chEBI ID':
                cheb_id = query_dict['value']
                where_clause = f"""
                FROM MetabolitePerExperiment
                WHERE cheb_id = '{cheb_id}'
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

