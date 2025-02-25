import re

import plotly.express as px
import numpy as np

from legacy.chart_data import get_chart_data
from models.experiment_df_wrapper import ExperimentDfWrapper

PLOTLY_TEMPLATE = 'plotly_white'


class ExperimentChartForm:
    @classmethod
    def from_df(cls, study_id, df):
        experiments = [e._asdict() for e in df.itertuples()]
        df_growth, df_reads = get_chart_data(study_id)

        return [cls(df_growth, df_reads, e) for e in experiments]

    def __init__(self, df_growth, df_reads, experiment):
        self.experiment_id    = experiment['experimentId']
        self.description      = experiment['experimentDescription']
        self.bioreplicate_ids = (experiment['bioreplicateIds'] or '').split(',')

        self.growth_data = ExperimentDfWrapper(df_growth, self.experiment_id, self.bioreplicate_ids)
        self.reads_data = ExperimentDfWrapper(df_reads, self.experiment_id, self.bioreplicate_ids)

        self.available_growth_techniques = [
            technique
            for technique in ['OD', 'Plate Counts', 'pH', 'FC']
            if technique in df_growth.keys()
        ]

        self.available_reads_techniques = []

        if self.reads_data.has_keys_matching('_counts'):
            self.available_reads_techniques.append('FC counts per species')
        if self.reads_data.has_keys_matching('_reads'):
            self.available_reads_techniques.append('Reads 16S rRNA Seq')

    def generate_growth_figures(self, measurement, args):
        selected_bioreplicate_ids, _ = self.extract_args(args)
        self.growth_data.select_bioreplicates(selected_bioreplicate_ids)

        fig = px.line(
            self.growth_data.df,
            x='Time',
            y=measurement,
            color='Biological_Replicate_id',
            title=f'{measurement} Plot for Experiment: {self.experiment_id} per Biological replicate',
            labels={'Time': 'Hours'},
            template=PLOTLY_TEMPLATE,
            markers=True
        )

        return [fig]

    def generate_reads_figures(self, read_type, args):
        selected_bioreplicate_ids, apply_log = self.extract_args(args)
        self.reads_data.select_bioreplicates(selected_bioreplicate_ids)

        figs = []
        for index, (bioreplicate_id, bioreplicate_df) in enumerate(self.reads_data.bioreplicate_dfs()):
            if read_type == 'reads':
                title = f'16S reads: {bioreplicate_id} per Microbial Strain'
                species_columns = bioreplicate_df.filter(regex='_reads$').columns
                std_columns = bioreplicate_df.filter(regex='_reads_std$').columns
            else:
                title = f'FC Counts: {bioreplicate_id} per Microbial Strain'
                species_columns = bioreplicate_df.filter(like='_counts').columns
                std_columns = None

            linear_y_label = 'Cells/mL'
            log_y_label = 'log(Cells)/mL'

            melted_df = bioreplicate_df.melt(
                id_vars=['Time', 'Biological_Replicate_id'],
                value_vars=sorted(species_columns),
                var_name='Species',
                value_name=linear_y_label
            )

            if apply_log[index]:
                # If we have 0 values, we'll get NaNs, which is okay for
                # rendering purposes, so we ignore the error:
                with np.errstate(divide='ignore'):
                    melted_df[log_y_label] = np.log10(melted_df[linear_y_label])

            melted_df['Species'] = melted_df['Species'].map(
                lambda s: re.sub(r'_(reads|counts)$', '', s)
            )
            error_y = None

            if std_columns is not None and not apply_log[index]:
                std_df = bioreplicate_df.melt(
                    id_vars=['Time', 'Biological_Replicate_id'],
                    value_vars=sorted(std_columns),
                    var_name='Species',
                    value_name='STD'
                )
                error_y = std_df['STD']

                if len(error_y) == 0:
                    # STD values were blank, don't draw error bars
                    error_y = None

            figs.append(px.line(
                melted_df,
                x='Time',
                y=(log_y_label if apply_log[index] else linear_y_label),
                error_y=error_y,
                color='Species',
                title=title,
                labels={'Time': 'Hours'},
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def generate_metabolite_figures(self, args):
        selected_bioreplicate_ids, _ = self.extract_args(args)
        self.growth_data.select_bioreplicates(selected_bioreplicate_ids)

        metabolite_keys = self.growth_data.get_metabolite_keys()

        figs = []
        for bioreplicate_id, bioreplicate_df in self.growth_data.bioreplicate_dfs():
            melted_df = bioreplicate_df.melt(
                id_vars=['Time', 'Biological_Replicate_id'],
                value_vars=metabolite_keys,
                var_name='Metabolites',
                value_name='mM'
            )

            figs.append(px.line(
                melted_df,
                x='Time',
                y='mM',
                color='Metabolites',
                title=f'Metabolite Concentrations: {bioreplicate_id} per Metabolite',
                labels={'Time': 'Hours'},
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def extract_args(self, args):
        selected_bioreplicate_ids = []
        include_average = False
        apply_log = [False for _ in args]

        for arg in args:
            if arg.endswith(':_average'):
                include_average = True
            elif arg.startswith('bioreplicate:'):
                selected_bioreplicate_ids.append(arg[len('bioreplicate:'):])
            elif arg.startswith('apply_log:'):
                index = int(arg[len('apply_log:'):])
                apply_log[index] = True

        if include_average:
            selected_bioreplicate_ids.append(f"Average {self.experiment_id}")

        return selected_bioreplicate_ids, apply_log
