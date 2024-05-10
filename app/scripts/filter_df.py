import pandas as pd

def filter_df(list_biorep_ids,df_growth,df_reads):
    result_growth_df = pd.DataFrame()
    result_reads_df = pd.DataFrame()
    if list_biorep_ids:
        if not df_growth.empty:
            #for now omit std to plot
            columns_to_keep = [col for col in df_growth.columns if not col.endswith('_std')]
            filtered_df = df_growth[columns_to_keep]
            result_growth_df = filtered_df[filtered_df['Bioloical_Replicate_id'].isin(list_biorep_ids)]
        if not df_growth.empty:
            columns_to_keep = [col for col in df_reads.columns if not col.endswith('_std')]
            filtered_df = df_reads[columns_to_keep]
            result_reads_df = filtered_df[filtered_df['Bioloical_Replicate_id'].isin(list_biorep_ids)]
    return result_growth_df, result_reads_df


def filter_dict_states(states):
    true_checkboxes ={}
    if states:
        true_checkboxes = {k:v for (k,v) in states.items() if v == True}
    return true_checkboxes