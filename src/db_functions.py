import os
import mysql.connector

user_name = os.environ.get('DB_USER')
password = os.environ.get('DB_PASSWORD')

DB_NAME = 'BacterialGrowth'

def execute(phrase):
    """
    This function create a connection to the database and execute a command.

    :param phrase: str SQL sentence to execute
    :return: list of str received from the database
    """
    try:
        cnx = mysql.connector.connect(user=user_name, password=password,host='localhost',database=DB_NAME)
        cnx.get_warnings = True
        cursor = cnx.cursor()
        cursor.execute(phrase)
        res = []
        for row in cursor:
            res.append(row)

        warnings = cursor.fetchwarnings()
        if warnings: 
            for i in range(len(warnings)):
                print("\t\t ** Warning - "+warnings[i][2])
        cursor.close()
        cnx.commit()
        cnx.close()
        return res
    except mysql.connector.Error as err:
        print("\nSomething went wrong: {}".format(err),'\n')
        exit()

def addRecord(table, args):
    """ 
    Add new entry into the db

    :param table: table of the DB
    :param args: dictionary with the data to insert (key = db field name. value = insert value)
    :return: id of the inserted record
    """
    # Insert into table
    fields, values = getInsertFieldsValues(args)
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

def countRecords(table, args):
    '''
    Count the records in one table for specific args

    :param table
    :param args: dictionary with the data to find and count (key = db field name. value = insert value)
    :return count int
    '''
    phrase = "SELECT COUNT(*) FROM " + table
    if args:
        where_clause = getWhereClause(args)
        phrase = phrase+" "+where_clause
    res = execute(phrase)
    return res[0][0]

def getAllRecords(table, args):
    '''
    Return all the records in one table for specific args

    :param table
    :param args: dictionary with the data to return (key = db field name. value = insert value)
    :return list of records
    '''
    phrase = "SELECT * FROM " + table
    if args:
        where_clause = getWhereClause(args)
        phrase = phrase+" "+where_clause
    res = execute(phrase)
    return res

def getFiles(fields, args):
    where_clause = getWhereClause(args)
    fields_clause = getSelectFields(fields)
    
    phrase = "SELECT "+fields_clause+" FROM TechnicalReplicate "+where_clause
    res = execute(phrase)
    return res

def getRecords(table, fields, args):
    where_clause = getWhereClause(args)
    fields_clause = getSelectFields(fields)
    
    phrase = "SELECT "+fields_clause+" FROM "+table+" "+where_clause
    res = execute(phrase)
    return res

# DATABASE SUPPLEMENTARY FUNCTIONS
# =================================

def getInsertFieldsValues(args):
    '''
    Create the fields and values strings to be inserted in the db
    
    :param args: dictionary with the data to return (key = db field name. value = insert value)
    :return str with part of query
    '''
    fields = "("
    values = "("
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    return [fields, values]

def getSelectFields(args):
    '''
    Create the str with the fields to be returned from db

    :args list or dictionary with fields to look for
    :return str clause
    '''
    clause = ""
    for field in args: 
        clause = clause + field + ", "
    clause = clause[:-2]
    return clause

def getWhereClause(args):
    '''
    Create the str with the where clause

    :args dictionary with the data to return (key = db field name. value = insert value)
    :return str clause
    '''
    if len(args) == 0:
        clause = ''
    else:
        clause = "WHERE ("
        for key, val in args.items():
            if val == 'null':
                clause = clause + key + " IS NULL AND "
            elif val == 'not null':
                clause = clause + key + " IS NOT NULL AND "
            else:
                clause = clause + key + "= '" + str(val) + "' AND "
        
        clause = clause[:-5] + ')'
    
    return clause

def getWhereInClause(args):
    '''
    Create the str with the where clause when it must contain and IN operator

    :args dictionary with the data to return (key = db field name. value = insert value)
    :return str clause
    '''
    if len(args) == 0:
        clause = ''
    else:
        clause = "WHERE ("
        for key, val in args.items():
            if key == 'bacteriaSpecies':
                val = str(val).replace(",)",")")
                clause = clause + key +" IN "+ str(val) + " AND "
            elif val == 'null':
                clause = clause + key + " IS NULL AND "
            elif val == 'not null':
                clause = clause + key + " IS NOT NULL AND "
            else:
                clause = clause + key + "= '" + str(val) + "' AND "
        
        clause = clause[:-5] + ')'
    
    return clause


def getJoinClause(table_from, table_to, field):
    '''
    Create the str with the join clause

    :param table_from and table_to: tables to be joined
    :param field: common field
    :return str clause
    '''
    clause = "JOIN "+table_to+" ON "+table_to+"."+field+" = "+table_from+"."+field
    return clause

def getGroupByClause(field):
    '''
    Get the str with the group by clause
    
    :param field
    :return str clause
    '''
    clause = "GROUP BY " + field
    return clause

def getHavingClause(agg_function, field, operator, quant, distinct=False):
    '''
    Get the str with the having clause
    
    :param agg_function: MIN(), MAX(), SUM(), AVG() or COUNT()
    :param field
    :param operator and quant: to build up the having condition. i.e. having id > 5
    :param distint: boolean if distinct must be added
    :return str clause
    '''
    clause = "HAVING "+agg_function
    if distinct == False:
        clause = clause + "("+field+") "+operator+" "+str(quant)
    elif distinct == True:
        clause = clause +"(DISTINCT "+field+") "+operator+" "+str(quant)
    return clause