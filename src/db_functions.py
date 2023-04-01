import os
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

from utils import getFieldsValues

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
    
    last_id = 0
    # What if INSERT IGNORE and it was not inserted?
    # https://stackoverflow.com/questions/6291405/mysql-after-insert-ignore-get-primary-key
    if "INSERT" in phrase:
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchall()[0][0]

    cursor.close()
    cnx.commit()
    cnx.close()
    return [last_id, res]

def addRecord(table, args):
    """ 
    This function adds a new entry into the indicated table.

    :table: table of the DB
    :args: dictionary with the data to insert
    :return: id of the inserted record
    """
    fields, values = getFieldsValues(args)
    phrase = "INSERT IGNORE INTO " + table + fields + " VALUES " + values
    last_id = execute(phrase)[0]
    return last_id

def countRecords(table, field, value):
    phrase = "SELECT COUNT(*) FROM "+table+" WHERE "+field+" = " + value
    res = execute(phrase)
    count = res[1][0][0]
    return count

# def getAllRecords(table):
#     phrase = "SELECT * FROM " + table
#     res = execute(phrase)
#     return res[1]

def getAllStudies():
    phrase = "SELECT * FROM Study"
    res = execute(phrase)
    return res[1]

def getAllExperiments(studyId):
    phrase = "SELECT * FROM Experiment WHERE studyId = '"+studyId+"';"
    res = execute(phrase)
    return res[1]

def getAllPerturbations(experimentId):
    phrase = "SELECT * FROM Perturbation WHERE experimentId = '"+experimentId+"';"
    res = execute(phrase)
    return res[1]

def getBacteria(bacteriaSpecies, *bacteriaStrain):
    bacteriaStrain = bacteriaStrain[0]
    if len(bacteriaStrain) == 0:
        phrase = "SELECT * FROM Bacteria WHERE bacteriaSpecies = '"+bacteriaSpecies+"';"
    else:
        phrase = "SELECT * FROM Bacteria WHERE bacteriaSpecies = '"+bacteriaSpecies+"' AND bacteriaStrain = '"+bacteriaStrain+"';"
    execute(phrase)