from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

config = {
  'user': 'root',
  'password': 'Pozuelo99.',
  'host': 'localhost',
  'database': 'bacteria_trial',
  'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()



# Create dictionary with the new tables
# =====================================
TABLES = {}
TABLES['Bacteria'] = (
    "CREATE TABLE `Bacteria` ("
    "  `bacteriaId` int NOT NULL AUTO_INCREMENT,"
    "  `bacteriaGenus` varchar(100) NOT NULL,"
    "  `bacteriaSpecies` varchar(100) NOT NULL,"
    "  `bacteriaStrain` varchar(100) NOT NULL,"
    "  PRIMARY KEY (`bacteriaId`)"
    ") ENGINE=InnoDB")

TABLES['Experiment'] = (
    "CREATE TABLE `Experiment` ("
    "  `experimentId` int NOT NULL AUTO_INCREMENT,"
    "  PRIMARY KEY (`experimentId`)"
    ") ENGINE=InnoDB")    

TABLES['Bacteria_Community'] = (
    "CREATE TABLE `Bacteria_Community` ("
    "  `communityId` int NOT NULL AUTO_INCREMENT,"
    "  `bacteriaId` int NOT NULL,"
    "  `experimentId` int NOT NULL,"
    "  PRIMARY KEY (`communityId`),"
    "  FOREIGN KEY (`bacteriaId`) REFERENCES Bacteria (`bacteriaId`),"
    "  FOREIGN KEY (`experimentId`) REFERENCES Experiment (`experimentId`)"
    ") ENGINE=InnoDB")


# Iterate over the dictionary to create the tables
# ================================================
for table_name in TABLES:
    table_description = TABLES[table_name]
    try:
        print("Creating table {}: ".format(table_name), end='')
        cursor.execute(table_description)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_TABLE_EXISTS_ERROR:
            print("already exists.")
        else:
            print(err.msg)
    else:
        print("OK")


cursor.close()
cnx.close()


