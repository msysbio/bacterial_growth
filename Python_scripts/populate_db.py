#!/usr/bin/env python3.6

import argparse
import mysql.connector
from mysql.connector import Error


parser = argparse.ArgumentParser()

parser.add_argument("--experiment_name",
                    
                    
                    )

parser.add_argument("--replicate",
                    type=int
                    
                    )

parser.add_argument("--bacteria",
                    "-b",
                    
                    
                    )

parser.add_argument("--strain",
                    "-s",
                    
                    )

parser.add_argument("--biculture",
                    action="store_true",
                    
                    )

parser.add_argument("--abundance_measurement",
                    
                    )

parser.add_argument("--units",
                    
                    )

parser.add_argument("--bacteria_growth_file"
)

parser.add_argument("--metabolites_growth_file"
)

parser.add_argument("--cultivation_technique"
)

parser.add_argument("--cultivation_medium_file"
)

parser.add_argument("--feeding_medium_file"
)

args = parser.parse_args()
experiment_name = args.experiment_name

# Connection to the DB

try:
    connection = mysql.connector.connect(host='localhost',
                                         database='bacterial_growth',
                                         user='root',
                                         password='')
    if connection.is_connected():
        db_Info = connection.get_server_info()
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor()
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
finally:
    if connection.is_connected():
        cursor.close()
        connection.close()
        print("MySQL connection is closed")



# Load into the DB the variables from args

# Maybe replicate can be autoincrement if we first look int the DB hown many instances with the same experiment_id we have.
