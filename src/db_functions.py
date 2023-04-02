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
    cnx = mysql.connector.connect(user=user_name, password=password,host='localhost',database=DB_NAME)
    cursor = cnx.cursor()
    cursor.execute(phrase)
    res = []
    for row in cursor:
        res.append(row)

    cursor.close()
    cnx.commit()
    cnx.close()
    return res

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



def countRecords(table, field, value):
    phrase = "SELECT COUNT(*) FROM "+table+" WHERE "+field+" = " + value
    res = execute(phrase)
    count = res[0][0]
    return count

# def getAllRecords(table):
#     phrase = "SELECT * FROM " + table
#     res = execute(phrase)
#     return res[1]

def getAllStudies():
    phrase = "SELECT * FROM Study"
    res = execute(phrase)
    return res

def getAllExperiments(studyId):
    phrase = "SELECT * FROM Experiment WHERE studyId = '"+studyId+"';"
    res = execute(phrase)
    return res

def getAllPerturbations(experimentId):
    phrase = "SELECT * FROM Perturbation WHERE experimentId = '"+experimentId+"';"
    res = execute(phrase)
    return res

def getBacteria(bacteriaSpecies, *bacteriaStrain):
    bacteriaStrain = bacteriaStrain[0]
    if len(bacteriaStrain) == 0:
        phrase = "SELECT * FROM Bacteria WHERE bacteriaSpecies = '"+bacteriaSpecies+"';"
    else:
        phrase = "SELECT * FROM Bacteria WHERE bacteriaSpecies = '"+bacteriaSpecies+"' AND bacteriaStrain = '"+bacteriaStrain+"';"
    execute(phrase)