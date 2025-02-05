import math
import os
import sys

import sqlalchemy as sql

filepath = os.path.realpath(__file__)
current_dir = os.path.dirname(filepath)
sys.path.append(current_dir)

APP_ENV = os.getenv('APP_ENV', 'development')


def getStudyID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Study;"
    number_projects = conn.execute(sql.text(query)).scalar()
    next_number = int(number_projects) + 1
    Study_ID = "SMGDB{:08d}".format(next_number)
    return Study_ID


def getChebiId(conn, metabolite):
    phrase = f"SELECT chebi_id FROM Metabolites WHERE metabo_name = '{metabolite}';"
    res = conn.execute(sql.text(phrase)).all()

    if len(res) == 0: return None

    return res[0][0]


# TODO (2024-10-20) This just raises errors, they need to be caught properly
def addRecord(conn, table, args):
    """
    Add new entry into the db

    :param table: table of the DB
    :param args: dictionary with the data to insert (key = db field name. value = insert value)
    :return: id of the inserted record
    """
    # Insert into table
    fields, values = getInsertFieldsValues(args)
    phrase = "INSERT INTO " +table+" "+fields+" VALUES "+values
    res = conn.execute(sql.text(phrase), args)

    # Get the name of the primary key field
    phrase = "SHOW KEYS FROM "+table+" WHERE Key_name = 'PRIMARY'"
    res = conn.execute(sql.text(phrase)).all()
    pk = res[0][4]

    # Get the value of the primary key (this will return the value both if it was inserted or ignored)
    where_clause = getWhereClause(args)
    phrase = "SELECT "+pk+" FROM "+table+" "+where_clause
    res = conn.execute(sql.text(phrase), args).all()

    if not res:
        raise Exception("No last_id returned")
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
        if type(val) is float and math.isnan(val):
            fields = fields + key + ','
            values = values + "NULL,"
        else:
            fields = fields + key + ','
            values = values + ":" + key + ','
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
            if val == 'null' or (type(val) is float and math.isnan(val)):
                clause = clause + key + " IS NULL AND "
            elif val == 'not null':
                clause = clause + key + " IS NOT NULL AND "
            else:
                clause = clause + key + "= :" + key + " AND "

        clause = clause[:-5] + ')'

    return clause

def getProjectID(conn):
    query = "SELECT IFNULL(COUNT(*), 0) FROM Project;"
    number_projects = conn.execute(sql.text(query)).scalar()
    next_number = int(number_projects) + 1
    Project_ID = "PMGDB{:06d}".format(next_number)
    return Project_ID
