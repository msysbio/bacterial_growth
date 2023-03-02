from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

import create_table
import insert_data
import get_data

# CREATE
TABLES = {}
query = "CREATE TABLE `Bacteria_Community` (`communityId` int NOT NULL AUTO_INCREMENT,`bacteriaId` int NOT NULL,`experimentId` int NOT NULL,PRIMARY KEY (`communityId`),FOREIGN KEY (`bacteriaId`) REFERENCES Bacteria (`bacteriaId`),FOREIGN KEY (`experimentId`) REFERENCES Experiment (`experimentId`)) ENGINE=InnoDB"
create_table.create(TABLES, 'Bacteria_Community', query)


# INSERT
insert_data.insert()

# QUERY
get_data.get()


