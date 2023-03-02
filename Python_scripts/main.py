from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

import create_table

config = {
  'user': 'root',
  'password': 'Pozuelo99.',
  'host': 'localhost',
  'database': 'bacteria_trial',
  'raise_on_warnings': True
}

cnx = mysql.connector.connect(**config)
cursor = cnx.cursor()

DB_NAME = 'bacteria_trial'

TABLES = {}

query = "CREATE TABLE `Bacteria_Community` (`communityId` int NOT NULL AUTO_INCREMENT,`bacteriaId` int NOT NULL,`experimentId` int NOT NULL,PRIMARY KEY (`communityId`),FOREIGN KEY (`bacteriaId`) REFERENCES Bacteria (`bacteriaId`),FOREIGN KEY (`experimentId`) REFERENCES Experiment (`experimentId`)) ENGINE=InnoDB"

create_table.create(cursor, DB_NAME, TABLES, 'Bacteria_Community', query)

cursor.close()
cnx.close()
