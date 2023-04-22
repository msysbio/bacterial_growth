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

def transformStringIntoList(string, ch):
    positions = findOccurrences(string, ch)
    list = []
    start = 0
    for i, pos in enumerate(positions):
        end = pos
        elem = string[start:end]
        list.append(elem)
        
        start = end + 1
        if string[start] == ' ':
            start = end + 2
    
    elem = string[start:]
    list.append(elem)
    
    return list

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
    
def getMeanStd(files, regex=''):
    '''
    This function gets a df and the columns (regex or all columns) in which mean and std are going to be calculated
    For each header, 
    '''
    df = pd.read_csv(files[0][0], sep=" ")
    
    if regex != '':
        headers = getMatchingList(regex, df)
    else:
        headers = df.columns
    
    msd = pd.DataFrame(columns=range(1))
    msd.set_axis(['time'], axis='columns', inplace=True)
    msd['time'] = df['time']
    
    for header in headers:
        if header != 'time':
            df_header = pd.DataFrame(columns=range(len(files)+1)) #Each column will be the value from each file

            # Fill the df parsing all the records' files
            for i, file in enumerate(files, 1):
                file_df = pd.read_csv(file[0], sep=" ")
                df_header.iloc[:,i] = file_df[header]

            # Calculate and keep mean and std
            msd_header = pd.DataFrame(columns=range(3))
            msd_header.set_axis(['time', header+'_mean', header+'_std'], axis='columns', inplace=True)
            msd_header['time'] = file_df['time']
            msd_header[header+'_mean'] = df_header.iloc[:,1:].mean(axis=1, numeric_only=True)
            msd_header[header+'_std'] = df_header.iloc[:,1:].std(axis=1, numeric_only=True)

            msd = pd.merge(msd, msd_header, on='time')
    
    return msd
