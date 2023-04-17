import os
import re
import pandas as pd

def isDir(string):
    '''
    This function checks if the given string is a directory path
    '''
    if os.path.isdir(string):
        return string
    else:
        raise NotADirectoryError(string)
    
def isFile(string):
    '''
    This function checks if the given string is a directory path
    '''
    if os.path.isfile(string):
        return string
    else:
        a = 0
        # Put warning or something here

def findOccurrences(string, ch):
    '''
    This function returns a list with all the positions of the string that contain the character ch
    '''
    return [i for i, letter in enumerate(string) if letter == ch]


def getMatchingList (regex, lst):
    '''
    This function takes a regex expression and returns a list with all the matching words in the given lst
    '''
    res = []
    for word in lst:
        if regex.findall(word):
            res.append(word)
    return res

def saveFile(data, path):
    if len(data.columns) > 1:
        data.to_csv(path, sep=" ", index=False)


def getIntersectionColumns(df, columns):
    res = df[df.columns.intersection(columns)]
    return res

def getFieldsValues(args):
    fields = "("
    values = "("
    for key, val in args.items():
        fields = fields + key + ','
        values = values + "'" +str(val) + "',"
    fields = fields[:-1] + ')'
    values = values[:-1] + ')'
    return [fields, values]

def getWhereClause(args):
    clause = "WHERE ("
    for key, val in args.items():
        if val != 'null':
            clause = clause + key + "= '" + str(val) + "' AND "
        if val == 'null':
            clause = clause + key + " IS NULL AND "
    clause = clause[:-5] + ')'
    return clause
    
def getMeanStd(records, header):
    df = pd.DataFrame(columns=range(len(records)+1)) #Each column will be the value of each record
    # Fill the df parsing all the records' files
    for i, record in enumerate(records, 1):
        record_df = pd.read_csv(record[0], sep=" ")
        df.iloc[:,i] = record_df[header]

    # Calculate and keep mean and std
    df_res = pd.DataFrame(columns=range(3))
    df_res.set_axis(['time', 'mean', 'std'], axis='columns', inplace=True)
    df_res['time'] = record_df['time']
    df_res['mean'] = df.iloc[:,1:].mean(axis=1, numeric_only=True)
    df_res['std'] = df.iloc[:,1:].std(axis=1, numeric_only=True)
    
    return df_res
