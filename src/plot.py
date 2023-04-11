import re
from prettytable import PrettyTable
import pandas as pd
import matplotlib.pyplot as plt

import db_functions as db
from user_inputs import *
from utils import getMatchingList, getIntersectionColumns

def chooseReplicates():
    study_id = chooseStudy()
    experiment_id = chooseExperiment(study_id)
    perturbation_id = choosePerturbation(experiment_id)

def plotOneReplicate():
    study_id = chooseStudy()
    experiment_id = chooseExperiment(study_id)
    perturbation_id = choosePerturbation(experiment_id)
    replicate_id = chooseReplicate(experiment_id=experiment_id, perturbation_id=perturbation_id)

    args = {
        'replicateId': replicate_id
        }
    
    # Abundance file
    # =====================================================================================
    abundance_file = db.getFiles('abundanceFile', args)
    abundance_df = pd.read_csv(abundance_file[0][0], sep=" ")

    od_regex = re.compile(r'.*time.* | .*OD.*', flags=re.I | re.X)
    count_regex = re.compile(r'.*time.* | .*count.*', flags=re.I | re.X)
    qpcr_regex = re.compile(r'.*time.* | .*qpcr.*', flags=re.I | re.X)
    rnaseq_regex = re.compile(r'.*time.* | .*rna.*', flags=re.I | re.X)

    od_headers = getMatchingList(od_regex, abundance_df)
    count_headers = getMatchingList(count_regex, abundance_df)
    qpcr_headers = getMatchingList(qpcr_regex, abundance_df)
    rnaseq_headers = getMatchingList(rnaseq_regex, abundance_df)

    od_data = getIntersectionColumns(abundance_df, od_headers)
    count_data = getIntersectionColumns(abundance_df, count_headers)
    qpcr_data = getIntersectionColumns(abundance_df, qpcr_headers)
    rnaseq_data = getIntersectionColumns(abundance_df, rnaseq_headers)

    plotSeveralColumns(od_data)
    plotSeveralColumns(count_data)
    plotSeveralColumns(qpcr_data)
    plotSeveralColumns(rnaseq_data)

    # Metabolites file
    # =====================================================================================
    metabolites_file = db.getFiles('metabolitesFile', args)
    metabolites_df = pd.read_csv(metabolites_file[0][0], sep=" ")

    plotSeveralColumns(metabolites_df)

    # pH file
    # =====================================================================================
    ph_file = db.getFiles('phFile', args)
    ph_df = pd.read_csv(ph_file[0][0], sep=" ")

    plotSeveralColumns(ph_df)

def plotMeanStdSeveralReplicates():
    study_id = chooseStudy()
    experiment_id = chooseExperiment(study_id)
    perturbation_id = choosePerturbation(experiment_id)

    args = {
        'perturbationId': perturbation_id
        }

    # Abundance file
    # =====================================================================================
    abundance_files = db.getFiles('abundanceFile', args)

    od_regex = re.compile(r'.*time.* | .*OD.*', flags=re.I | re.X)
    count_regex = re.compile(r'.*time.* | .*count.*', flags=re.I | re.X)
    qpcr_regex = re.compile(r'.*time.* | .*qpcr.*', flags=re.I | re.X)
    rnaseq_regex = re.compile(r'.*time.* | .*rna.*', flags=re.I | re.X)

    od_msd = getMeanStd(abundance_files, regex=od_regex)
    count_msd = getMeanStd(abundance_files, regex=count_regex)
    qpcr_msd = getMeanStd(abundance_files, regex=qpcr_regex)
    rnaseq_msd = getMeanStd(abundance_files, regex=rnaseq_regex)

    plotSeveralMeanStd(od_msd)
    plotSeveralMeanStd(count_msd)
    plotSeveralMeanStd(qpcr_msd)
    plotSeveralMeanStd(rnaseq_msd)

    # Metabolites file
    # =====================================================================================
    metabolites_files = db.getFiles('metabolitesFile', args)
    metabolites_msd = getMeanStd(metabolites_files, regex='')
    plotSeveralMeanStd(metabolites_msd)

    # pH file
    # =====================================================================================
    ph_files = db.getFiles('phFile', args)
    ph_msd = getMeanStd(ph_files, regex='')
    plotSeveralMeanStd(ph_msd)

def plotSeveralColumns(df):
    if len(df.columns) > 1:
        for column in df:
            if column != 'time':
                plt.plot('time', column, data=df, linestyle='-')
        plt.legend()
        plt.show()

def plotSeveralMeanStd(dfs):
    if len(dfs.columns) > 1:
        fig = plt.figure()
        ax = fig.add_subplot(111)
        # ax.set_xlabel('time', fontsize = 16)
        # ax.set_ylabel('abundance', fontsize = 16)

        cmap = plt.get_cmap(name='tab10')

        for i in range(1,len(dfs.columns),2):
            ax.errorbar(dfs.iloc[:,0], dfs.iloc[:,i], yerr = dfs.iloc[:,i+1], color = cmap(i-1))

        plt.show()

def getMeanStd(records, regex=''):
    record = pd.read_csv(records[0][0], sep=" ")
    
    if regex != '':
        headers = getMatchingList(regex, record)
    else:
        headers = record.columns
    
    dfs = pd.DataFrame(columns=range(1))
    dfs.set_axis(['time'], axis='columns', inplace=True)
    dfs['time'] = record['time']
    
    for header in headers:
        if header != 'time':
            df = pd.DataFrame(columns=range(len(records)+1)) #Each column will be the value of each record

            # Fill the df parsing all the records' files
            for i, record in enumerate(records, 1):
                record_df = pd.read_csv(record[0], sep=" ")
                df.iloc[:,i] = record_df[header]

            # Calculate and keep mean and std
            df_res = pd.DataFrame(columns=range(3))
            df_res.set_axis(['time', header+'_mean', header+'_std'], axis='columns', inplace=True)
            df_res['time'] = record_df['time']
            df_res[header+'_mean'] = df.iloc[:,1:].mean(axis=1, numeric_only=True)
            df_res[header+'_std'] = df.iloc[:,1:].std(axis=1, numeric_only=True)

            dfs = pd.merge(dfs, df_res, on='time')
    
    return dfs