import re
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.legend import Legend

import db_functions as db
from user_inputs import *
from utils import getMatchingList, getIntersectionColumns, getMeanStd

from constants import *

def plot(option):
    '''
    This function takes the user plot choice, makes the user choose the data to plot (form the args dictionary) and call the corresponding functions
    '''
    fields = ['abundance', 'metabolites', 'ph']
    if option == '1':
        # Only one replicate
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)
        perturbation_id = choosePerturbation(experiment_id)
        if perturbation_id == '0':
            replicate_id = chooseReplicate(experiment_id=experiment_id, perturbation_id=None)
        else:
            replicate_id = chooseReplicate(experiment_id=experiment_id, perturbation_id=perturbation_id)

        args = {'replicateId': replicate_id}
        
    
    if option == '2':
        # Several replicates from same perturbation
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)
        perturbation_id = choosePerturbation(experiment_id)

        if perturbation_id == '0':
            args = {'experimentId': experiment_id, 'perturbationId': 'null'}
        else:
            args = {'perturbationId': perturbation_id}

    
    if option == '3':
        # Several replicates from same experiment and different perturbations
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        experiment_id = chooseExperiment(study_id)

        args = {'experimentId': experiment_id}
        

    plotAbundances(args)
    plotMetabolites(args)
    plotPh(args)
    

def plotAbundances(args):
    '''
    Plot abundances.
    As there are different measurements, it plots them separately
    '''
    files = db.getFiles({'abundanceFile'}, args)
    if len(files) == 1:
        for opt in abundance_options:
            regex = globals()['%s_regex' % opt]
            plotOneReplicate(files, regex=regex, db_field={'abundanceFile'})
            
    elif len(files) > 1:
        for opt in abundance_options:
            regex = globals()['%s_regex' % opt]
            plotExperimentPerturbation(args, regex=regex, db_field={'abundanceFile'})
                
    
def plotMetabolites(args):
    '''
    Plot metabolites
    '''
    files = db.getFiles({'metabolitesFile'}, args)
    if len(files) == 1:
        plotOneReplicate(files, regex='', db_field={'metabolitesFile'})
            
    elif len(files) > 1:
        plotExperimentPerturbation(args, regex='', db_field={'metabolitesFile'})
    
    
def plotPh(args):
    '''
    Plot ph
    '''
    files = db.getFiles({'phFile'}, args)
    if len(files) == 1:
        plotOneReplicate(files, regex='', db_field={'phFile'})
            
    elif len(files) > 1:
        plotExperimentPerturbation(args, regex='', db_field={'phFile'})


def plotExperimentPerturbation(args, regex='', db_field={}):
    '''
    Plot if there are several replicates
    Analyzes the data. Replicates can be from experiments and/or perturbation
    '''
    
    label_ids = []
    
    if 'experimentId' in args:
        exp_with_null = db.countRecords('TechnicalReplicate', {'experimentId': args['experimentId']})
        exp_without_null = db.countRecords('TechnicalReplicate', {'experimentId': args['experimentId'], 'perturbationId': 'null'})
    else:
        exp_with_null = 0
        exp_without_null = 0
    
    if exp_with_null != exp_without_null and exp_with_null > 0 and exp_without_null > 0:
        perturbation_ids = db.getRecords('Perturbation', {'perturbationId'}, args)
        
        cnt = 0
        # Plot: ==================================================================================================================
        fig = plt.figure()
        ax = fig.add_subplot()
        
        # Experiment data
        args2 = args.copy()
        args2['perturbationId'] = 'null'
        files = db.getFiles(db_field, args2)
        plot, vec = plotSetReplicates(files, regex, ax, cnt)
        cnt = cnt + 1
        label = 'Experiment id ' + args['experimentId']
        label_ids.append(label)
        
         # Perturbation data
        for perturbation_id in perturbation_ids:
            files = db.getFiles(db_field, {'perturbationId': perturbation_id[0]})
            plot, vec = plotSetReplicates(files, regex, ax, cnt)
            cnt = cnt + 1
            label = 'Perturbation id ' + perturbation_id[0]
            label_ids.append(label)
            
        # Legend: =========================================================
        if plot != None:
            handles, labels = ax.get_legend_handles_labels()
            legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
            legend2 = getExperimentLegend(ax, handles, label_ids, vec)
            ax.add_artist(legend2)
        # =================================================================
        
        ax.set_xlabel('time')
        ax.set_ylabel(list(db_field)[0][:-4])
        plt.show()
        # ========================================================================================================================
        
    else:
        perturbation_ids = db.getRecords('Perturbation', {'perturbationId'}, args)
        
        if len(perturbation_ids) == 0:
            files = db.getFiles(db_field, args)
            
            cnt = 0
            # Plot: ==================================================================================================================
            fig = plt.figure()
            ax = fig.add_subplot()
            
            # Experiment data
            plot, vec = plotSetReplicates(files, regex, ax, cnt)
            cnt = cnt + 1
            label = 'Experiment id ' + args['experimentId']
            label_ids.append(label)
            
            # Legend: =========================================================
            if plot != None:
                handles, labels = ax.get_legend_handles_labels()
                legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
                legend2 = getExperimentLegend(ax, handles, label_ids, vec)
                ax.add_artist(legend2)
            # =================================================================
            
            ax.set_xlabel('time')
            ax.set_ylabel(list(db_field)[0][:-4])
            plt.show()
            # ========================================================================================================================
            
        else:
            cnt = 0
            # Plot: ==================================================================================================================
            fig = plt.figure()
            ax = fig.add_subplot()
            
            # Perturbation data
            for perturbation_id in perturbation_ids:
                files = db.getFiles(db_field, {'perturbationId': perturbation_id[0]})
                plot, vec = plotSetReplicates(files, regex, ax, cnt)
                cnt = cnt + 1
                label = 'Perturbation id ' + perturbation_id[0]
                label_ids.append(label)
            
            # Legend: =========================================================
            if plot != None:
                handles, labels = ax.get_legend_handles_labels()
                legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
                legend2 = getExperimentLegend(ax, handles, label_ids, vec)
                ax.add_artist(legend2)
            # =================================================================
            
            ax.set_xlabel('time')
            ax.set_ylabel(list(db_field)[0][:-4])
            plt.show()
            # ========================================================================================================================

def plotOneReplicate(files, regex='', db_field=''):
    df = pd.read_csv(files[0][0], sep=" ")
    
    if regex != '': headers = getMatchingList(regex, df)
    else: headers = df.columns
    
    data = getIntersectionColumns(df, headers)
            
    # Plot: ==================================================================================================================
    fig = plt.figure()
    ax = fig.add_subplot()
    if len(data.columns)>1: 
        plot, vec = plotDf(data, ax)
    else: 
        plot = plt.close()
        vec = range(0,0,1)
    
    # Legend: =========================================================
    if plot != None:
        handles, labels = ax.get_legend_handles_labels()
        ax.legend(labels, loc='upper right')
    # =================================================================
    
    ax.set_xlabel('time')
    ax.set_ylabel(list(db_field)[0][:-4])
    plt.show()
    # ========================================================================================================================
    
    return plot, vec

def plotSetReplicates(files, regex, ax, count):
    data = getMeanStd(files, regex)
        
    if len(data.columns)>1: 
        plot, vec = plotDf(data, ax, count)
    else: 
        plot = plt.close()
        vec = range(0,0,1)
    
    return plot, vec

def plotDf(df, ax, style_count=0):
    cmap = plt.get_cmap(name='tab10')
    styles = ['-', '--', '-.', ':', '-x', '-o', '-<', '->']
    
    msd_regex = re.compile(r'.*mean.* | .*std.*', flags=re.I | re.X)
    
    if len(getMatchingList(msd_regex, df)) > 0:
        vec = range(1,len(df.columns),2)
        for i in vec:
            plot = ax.errorbar(df.iloc[:,0], df.iloc[:,i], yerr = df.iloc[:,i+1], fmt=styles[style_count], color = cmap(i-1), label=df.columns[i][:-5])
    else:
        vec = range(1,len(df.columns))
        for i in vec:
            plot = ax.plot(df.iloc[:,0], df.iloc[:,i], linestyle=styles[style_count], color = cmap(i-1), label=df.columns[i])
    return plot, vec


def getExperimentLegend(ax, handles, labels, vec):
    vec1 = [*range(0,len(labels))]
    vec2 = [x * len(vec) for x in vec1]
    new_handles = [handles[i] for i in vec2]
    leg = Legend(ax, new_handles, labels, frameon=False, bbox_to_anchor=(1.04, 1), loc='lower right')
    return leg