import pandas as pd

def filter_df(experiment_with_bioreps,df_growth,df_reads):
    result_growth_df_dict = {}
    result_reads_df_dict = {}
    if experiment_with_bioreps:
        if not df_growth.empty:
            #for now omit std to plot
            columns_to_keep = [col for col in df_growth.columns if not col.endswith('_std')]
            print("columns_to_keep",columns_to_keep)
            filtered_df = df_growth[columns_to_keep]
            print(filtered_df)
            for exp, biorep in experiment_with_bioreps.items():
                fil = filtered_df[filtered_df['Biological_Replicate_id'].isin(biorep)]
                print(biorep,fil)
                result_growth_df_dict[exp]=fil
        if not df_reads.empty:
            columns_to_keep = [col for col in df_reads.columns if not col.endswith('_std')]
            filtered_df = df_reads[columns_to_keep]
            print(filtered_df)
            for exp, biorep in experiment_with_bioreps.items():
                result_reads_df_dict[exp]=filtered_df[filtered_df['Biological_Replicate_id'].isin(biorep)]
    return result_growth_df_dict, result_reads_df_dict


def filter_dict_states(states):
    true_checkboxes ={}
    experiment_with_bioreps = {}
    if states:
        true_checkboxes = {k:v for (k,v) in states.items() if k.startswith('checkbox') and v == True}
        for k in true_checkboxes.keys():
            parts = k.split(':biologicalreplicate:')
            experiment_name = parts[0].replace('checkbox', '')
            biorep_id = parts[1]
            if experiment_name in experiment_with_bioreps:
                experiment_with_bioreps[experiment_name].append(biorep_id)
            else:
                experiment_with_bioreps[experiment_name] = [biorep_id]
    return experiment_with_bioreps