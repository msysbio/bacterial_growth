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

    :param option: str
    '''
    fields = ['abundance', 'metabolites', 'ph']
    if option == '1':
        # Only one replicate
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        biological_id = chooseBiologicalReplicate(study_id)
        perturbation_id = choosePerturbation(biological_id)
        if perturbation_id == 0:
            technical_id = chooseReplicate(biological_id=biological_id, perturbation_id=None)
        else:
            technical_id = chooseReplicate(biological_id=biological_id, perturbation_id=perturbation_id)

        args = {'technicalReplicateId': technical_id}
        
    
    if option == '2':
        # Several replicates from same perturbation
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        biological_id = chooseBiologicalReplicate(study_id)
        perturbation_id = choosePerturbation(biological_id)

        if perturbation_id == 0:
            args = {'biologicalReplicateId': biological_id, 'perturbationId': 'null'}
        else:
            args = {'perturbationId': perturbation_id}

    
    if option == '3':
        # Several replicates from same biological replicate and different perturbations
        # --------------------------------------------------------------------------------------------------------
        study_id = chooseStudy()
        biological_id = chooseBiologicalReplicate(study_id)

        args = {'biologicalReplicateId': biological_id}
        

    plotAbundances(args)
    plotMetabolites(args)
    plotPh(args)
    
def plotAbundances(args):
    '''
    Plot abundances. As there are different measurements, it plots them separately

    :param args: user input to plot
    '''
    files = db.getFiles({'abundanceFile'}, args)
    if len(files) == 1:
        for opt in abundance_options:
            regex = globals()['%s_regex' % opt]
            plotOneReplicate(files, regex=regex, db_field={'abundanceFile'})
            
    elif len(files) > 1:
        for opt in abundance_options:
            regex = globals()['%s_regex' % opt]
            plotBiologicalReplicatePerturbation(args, regex=regex, db_field={'abundanceFile'})
                    
def plotMetabolites(args):
    '''
    Plot metabolites

    :param args: user input to plot
    '''
    files = db.getFiles({'metabolitesFile'}, args)
    if len(files) == 1:
        plotOneReplicate(files, regex='', db_field={'metabolitesFile'})
            
    elif len(files) > 1:
        plotBiologicalReplicatePerturbation(args, regex='', db_field={'metabolitesFile'})
        
def plotPh(args):
    '''
    Plot ph

    :param args: user input to plot
    '''
    files = db.getFiles({'phFile'}, args)
    if len(files) == 1:
        plotOneReplicate(files, regex='', db_field={'phFile'})
            
    elif len(files) > 1:
        plotBiologicalReplicatePerturbation(args, regex='', db_field={'phFile'})

def plotBiologicalReplicatePerturbation(args, regex='', db_field={}):
    '''
    Plot if there are several replicates
    Analyzes the data. Replicates can be from biological replicates and/or perturbation

    :param args: user input to plot
    :param regex. if abundance, to separate in the different measurements
    :param db_field: abundanceFile, metabolitesFile or phFile
    '''
    
    label_ids = []
    
    if 'biologicalReplicateId' in args:
        biol_rep_with_null = db.countRecords('TechnicalReplicate', {'biologicalReplicateId': args['biologicalReplicateId']})
        biol_rep_without_null = db.countRecords('TechnicalReplicate', {'biologicalReplicateId': args['biologicalReplicateId'], 'perturbationId': 'null'})
    else:
        biol_rep_with_null = 0
        biol_rep_without_null = 0
    
    if biol_rep_with_null != biol_rep_without_null and biol_rep_with_null > 0 and biol_rep_without_null > 0:
        perturbation_ids = db.getRecords('Perturbation', {'perturbationId'}, args)
        
        cnt = 0
        # Plot: ==================================================================================================================
        fig = plt.figure()
        ax = fig.add_subplot()
        
        # BiologicalReplicate data
        args2 = args.copy()
        args2['perturbationId'] = 'null'
        files = db.getFiles(db_field, args2)
        plot, vec = plotSetReplicates(files, regex, ax, cnt)
        cnt = cnt + 1
        label = 'BiologicalReplicate id ' + args['biologicalReplicateId']
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
            legend2 = getBiologicalReplicateLegend(ax, handles, label_ids, vec)
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
            
            # BiologicalReplicate data
            plot, vec = plotSetReplicates(files, regex, ax, cnt)
            cnt = cnt + 1
            label = 'BiologicalReplicate id ' + args['biologicalReplicateId']
            label_ids.append(label)
            
            # Legend: =========================================================
            if plot != None:
                handles, labels = ax.get_legend_handles_labels()
                legend1 = ax.legend(labels[0:len([*vec])], loc='upper right')
                legend2 = getBiologicalReplicateLegend(ax, handles, label_ids, vec)
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
                legend2 = getBiologicalReplicateLegend(ax, handles, label_ids, vec)
                ax.add_artist(legend2)
            # =================================================================
            
            ax.set_xlabel('time')
            ax.set_ylabel(list(db_field)[0][:-4])
            plt.show()
            # ========================================================================================================================

def plotOneReplicate(files, regex='', db_field=''):
    '''
    If plotting a single file

    :param files corresponding to user choice
    :param regex. if abundance, to separate in the different measurements
    :param db_field: abundanceFile, metabolitesFile or phFile
    '''
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
    '''
    If plottig several files

    :param files corresponding to user choice
    :param regex. if abundance, to separate in the different measurements
    :param ax: matplotlib axis to hold on plot
    :param count: as we plot several files count to differentiate line styles
    '''
    data = getMeanStd(files, regex)
        
    if len(data.columns)>1: 
        plot, vec = plotDf(data, ax, count)
    else: 
        plot = plt.close()
        vec = range(0,0,1)
    
    return plot, vec

def plotDf(df, ax, style_count=0):
    '''
    Finally plot into the axis

    :param df
    :param ax: matplotlib axis
    :param style_count: int to select the line style
    '''
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


def getBiologicalReplicateLegend(ax, handles, labels, vec):
    '''
    Add legend

    :param ax: matplotlib axis
    :param handles: list of elements that have been plotted in ax
    :param labels: list of labels of the plotted elements (handles)
    :param vec: vector to select which labels to add in the legend
    :return legend
    '''
    vec1 = [*range(0,len(labels))]
    vec2 = [x * len(vec) for x in vec1]
    new_handles = [handles[i] for i in vec2]
    leg = Legend(ax, new_handles, labels, frameon=False, bbox_to_anchor=(1.04, 1), loc='lower right')
    return leg