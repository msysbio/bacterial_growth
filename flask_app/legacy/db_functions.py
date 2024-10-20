import os
import sys
import tomllib
from pathlib import Path

import sqlalchemy as sql
import mysql.connector

filepath = os.path.realpath(__file__)
current_dir = os.path.dirname(filepath)
sys.path.append(current_dir)

# This directory MUST BE the one where the core is in the server
APP_ENV = os.getenv('APP_ENV', 'development')

def getStudyID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Study;"
    number_projects = conn.execute(sql.text(query)).scalar()
    next_number = int(number_projects) + 1
    Study_ID = "SMGDB{:08d}".format(next_number)
    return Study_ID

def getChebiId(metabolite):
    phrase = f"SELECT cheb_id FROM Metabolites WHERE metabo_name = '{metabolite}';"
    res = execute(phrase)

    if len(res) == 0: return None

    return res[0][0]

# TODO (2024-10-20) Need to get this to work with sqlalchemy
def execute(phrase):
    """
    This function create a connection to the database and execute a command.

    :param phrase: str SQL sentence to execute
    :return: list of str received from the database
    """
    try:
        config = tomllib.loads(Path('config/database.toml').read_text())
        env_config = config[APP_ENV]

        cnx = mysql.connector.connect(
            **env_config,
        )

        cursor = cnx.cursor()
        cursor.execute(phrase)
        # return cursor
        res = []
        for row in cursor:
            res.append(row)
        # return res
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
        return err

def addRecord(table, args):
    """
    Add new entry into the db

    :param table: table of the DB
    :param args: dictionary with the data to insert (key = db field name. value = insert value)
    :return: id of the inserted record
    """
    # Insert into table
    fields, values = getInsertFieldsValues(args)
    phrase = "INSERT IGNORE INTO " +table+" "+fields+" VALUES "+values
    res = execute(phrase)

    # Get the name of the primary key field
    phrase = "SHOW KEYS FROM "+table+" WHERE Key_name = 'PRIMARY'"
    res = execute(phrase)
    pk = res[0][4]

    # Get the value of the primary key (this will return the value both if it was inserted or ignored)
    where_clause = getWhereClause(args)
    phrase = "SELECT "+pk+" FROM "+table+" "+where_clause
    res = execute(phrase)
    if not res:
        last_id = 'WARNING'
    else:
        last_id = res[0][0]

    return last_id

# # DATABASE SUPPLEMENTARY FUNCTIONS
# # =================================

def getInsertFieldsValues(args):
    '''
    Create the fields and values strings to be inserted in the db

    :param args: dictionary with the data to return (key = db field name. value = insert value)
    :return str with part of query
    '''
    if len(args) == 0:
        return ['', '']

    fields = "("
    values = "("
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    return [fields, values]

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

def getProjectID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Project;"
    number_projects = conn.execute(sql.text(query)).scalar()
    next_number = int(number_projects) + 1
    Project_ID = "PMGDB{:06d}".format(next_number)
    return Project_ID
