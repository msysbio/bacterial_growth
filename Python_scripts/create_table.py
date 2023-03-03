from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

def create(TABLES, table_name, query):

    cnx = mysql.connector.connect(user='root', password='XXX',host='localhost',database='bacteria_trial')
    cursor = cnx.cursor()

    TABLES[table_name] = (query)

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
