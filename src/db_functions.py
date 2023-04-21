import os
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

from utils import getFieldsValues, getWhereClause

user_name = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')

DB_NAME = 'BacterialGrowth'

def execute(phrase):
    """This function create a connection to the database and execute a command.
    :param phrase: str SQL sentence to execute
    :return: list of str received from the database after command execution.
    """
    try:
        cnx = mysql.connector.connect(user=user_name, password=password,host='localhost',database=DB_NAME)
        cnx.get_warnings = True
        cursor = cnx.cursor()
        cursor.execute(phrase)
        res = []
        for row in cursor:
            res.append(row)

        warnings = cursor.fetchwarnings()
        if warnings: 
            for i in range(len(warnings)):
                print("\t ** Warning - "+warnings[i][2])
        cursor.close()
        cnx.commit()
        cnx.close()
        return res
    except mysql.connector.Error as err:
        print("Something went wrong: {}".format(err))
        print(phrase)

def addRecord(table, args):
    """ 
    This function adds a new entry into the indicated table.

    :table: table of the DB
    :args: dictionary with the data to insert
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
    last_id = res[0][0]
    
    return last_id

def countRecords(table, args):
    phrase = "SELECT COUNT(*) FROM " + table
    if args:
        where_clause = getWhereClause(args)
        phrase = phrase+" "+where_clause
    res = execute(phrase)
    return res

def getAllRecords(table, **args):
    phrase = "SELECT * FROM " + table
    if args:
        where_clause = getWhereClause(args)
        phrase = phrase+" "+where_clause
    res = execute(phrase)
    return res

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

# DATABASE SUPPLEMENTARY FUNCTIONS
# =================================

def getInsertFieldsValues(args):
    fields = "("
    values = "("
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    return [fields, values]

def getSelectFields(args):
    clause = ""
    for field in args: 
        clause = clause + field + ", "
    clause = clause[:-2]
    return clause

def getWhereClause(args):
    if len(args) == 0:
        clause = ''
    else:
        clause = "WHERE ("
        for key, val in args.items():
            if key == 'bacteriaSpecies':
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
    clause = "JOIN "+table_to+" ON "+table_to+"."+field+" = "+table_from+"."+field
    return clause

def getGroupByClause(field):
    clause = "GROUP BY " + field
    return clause

def getHavingClause(agg_function, field, operator, quant, distinct=False):
    clause = "HAVING "+agg_function
    if distinct == False:
        clause = clause + "("+field+") "+operator+" "+str(quant)
    elif distinct == True:
        clause = clause +"(DISTINCT "+field+") "+operator+" "+str(quant)
    return clause