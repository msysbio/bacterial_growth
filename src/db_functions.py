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
    fields, values = getFieldsValues(args)
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

def getFiles(field, args):
    where_clause = getWhereClause(args)
    phrase = "SELECT "+field+" FROM TechnicalReplicate "+where_clause
    res = execute(phrase)
    return res

def getRecords(table, field, args):
    where_clause = getWhereClause(args)
    phrase = "SELECT "+field+" FROM "+table+" "+where_clause
    res = execute(phrase)
    return res