from __future__ import print_function
import mysql.connector
from mysql.connector import errorcode

def insert():

    cnx = mysql.connector.connect(user='root', password='',host='localhost',database='bacteria_trial')
    cursor = cnx.cursor()

    # FORMAT 1
    add_bacteria = ("INSERT INTO Bacteria "
                "(bacteriaGenus, bacteriaSpecies, bacteriaStrain) "
                "VALUES (%s, %s, %s)")

    data_bacteria = ('Bacteroides', 'Bacteroides thetaiotaomicron', 'VPI 5482')

    # add_bacteria = ("INSERT INTO Bacteria "
    #             "(bacteriaGenus, bacteriaSpecies)"
    #             "VALUES (%s, %s)")

    # data_bacteria = ('Bacteroides', 'Bacteroides thetaiotaomicron')

    cursor.execute(add_bacteria, data_bacteria)
    # emp_no = cursor.lastrowid # To use it in the next table (salaries for the FK)

    # # FORMAT 2 - extended Python format codes
    # add_salary = ("INSERT INTO salaries "
    #             "(emp_no, salary, from_date, to_date) "
    #             "VALUES (%(emp_no)s, %(salary)s, %(from_date)s, %(to_date)s)")

    # data_salary = {
    #     'emp_no': emp_no,
    #     'salary': 50000,
    #     'from_date': tomorrow,
    #     'to_date': date(9999, 1, 1),
    # }
    # cursor.execute(add_salary, data_salary)

    # Make sure data is committed to the database
    cnx.commit()

    cursor.close()
    cnx.close()
