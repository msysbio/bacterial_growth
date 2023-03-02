from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

def get():

    cnx = mysql.connector.connect(user='root', password='Pozuelo99.',host='localhost',database='bacteria_trial')
    cursor = cnx.cursor()

    query = ("SELECT bacteriaSpecies FROM Bacteria WHERE bacteriaGenus = %s")

    bacteriaGenus_1 = "Bacteroides"

    cursor.execute(query, bacteriaGenus_1)

    for (bacteriaSpecies) in cursor:
        print("{}".format(bacteriaSpecies))

    cursor.close()
    cnx.close()


