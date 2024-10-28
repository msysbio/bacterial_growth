import pandas as pd


class ExperimentDfWrapper:
    def __init__(self, df, experiment_id, bioreplicate_ids):
        self.df = df
        self.experiment_id = experiment_id
        self.experiment_bioreplicate_ids = bioreplicate_ids

    def keys(self):
        return self.df.keys()

    def drop_columns(self, *args):
        self.df = self.df[self.df.columns.drop(*args)]

    def has_keys_matching(self, string):
        return any(k for k in self.keys() if k.find(string) >= 0)

    def bioreplicate_dfs(self):
        return self.df.groupby('Biological_Replicate_id')

    def get_metabolite_keys(self):
        non_metabolite_keys = {
            'Position', 'Biological_Replicate_id', 'Time',
            'OD', 'Plate Counts', 'pH', 'FC',
        }
        return set(self.df.keys()).difference(non_metabolite_keys)

    def get_measurement_keys(self):
        measurement_keys = {'OD', 'Plate Counts', 'pH', 'FC'}
        return set(self.df.keys()).intersection(measurement_keys)

    def reorder_columns(self, new_column_list):
        self.df = self.df[new_column_list]

    def rename_columns(self, renamer):
        self.df = self.df.rename(columns=renamer)

    def select_bioreplicates(self, selected_bioreplicate_ids):
        if f"Average {self.experiment_id}" in selected_bioreplicate_ids:
            numeric_cols = self.df.select_dtypes(include='number').columns.drop('Time')

            experiment_data = self.df[self.df['Biological_Replicate_id'].isin(self.experiment_bioreplicate_ids)]
            mean_df_specific_ids = experiment_data.groupby('Time')[numeric_cols].mean().reset_index()
            mean_df_specific_ids['Biological_Replicate_id'] = f"Average {self.experiment_id}"

            self.df = pd.concat([self.df, mean_df_specific_ids], ignore_index=True)

        self.df = self.df[self.df['Biological_Replicate_id'].isin(selected_bioreplicate_ids)]
