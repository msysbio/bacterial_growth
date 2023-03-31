import os
import mysql.connector
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import re

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
    if "INSERT" in phrase:
        cursor.execute("SELECT LAST_INSERT_ID()")
        last_id = cursor.fetchall()[0][0]

    cursor.close()
    cnx.commit()
    cnx.close()
    return [last_id, res]

def addStudy(args):
    """ 
    This function creates a new experiment.

    :params: dictionary of fields to introduce in the table
    :return: id of the inserted record
    """
    fields = "("
    values = "("
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    phrase = "INSERT INTO Study " + fields + " VALUES " + values
        
    last_id = execute(phrase)[0]
    return last_id

def addExperiment(expId, studyId, args):
    """ 
    This function adds some cultivation conditions to an existing experiment.

    :params: experimentId, studyId, dictionary of parameters
    :return: id of the inserted record
    """
    fields = "(experimentId,studyId,"
    values = "("+expId+","+studyId+","
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    phrase = "INSERT IGNORE INTO Experiment " + fields + " VALUES " + values

    last_id = execute(phrase)[0]
    return last_id

def addPerturbation(pertId, expId, args):
    """ 
    This function adds some cultivation conditions to an existing experiment.

    :params: experimentId, studyId, dictionary of parameters
    :return: id of the inserted record
    """
    fields = "(perturbationId,experimentId,"
    values = "("+pertId+","+expId+","
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    phrase = "INSERT IGNORE INTO Perturbation " + fields + " VALUES " + values

    last_id = execute(phrase)[0]
    return last_id
    






def addReplicate(repId, cultId):
    phrase = "INSERT IGNORE INTO TechnicalReplicates (replicateId, cultivationId) VALUES ('"+repId+"','"+cultId+"')"
    last_id = execute(phrase)[0]
    return last_id

def addReplicateFile(repId, **file):
    for key, val in file.items():
        phrase = "UPDATE TechnicalReplicates SET "+key+" = '"+val+"' WHERE replicateId = '"+repId+"'"
        execute(phrase)
    
def addBacteria(bacteriaSpecies, bacteriaStrain):
    return False

def countRecords(table, field, value):
    phrase = "SELECT COUNT(*) FROM "+table+" WHERE "+field+" = " + value
    res = execute(phrase)
    count = res[1][0][0]
    return count

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