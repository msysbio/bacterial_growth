import plotly.express as px

from flask_app.lib.hack import get_chart_data
from flask_app.models.experiment_df_wrapper import ExperimentDfWrapper

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
        self.bioreplicate_ids = experiment['bioreplicateIds'].split(',')

        self.growth_data = ExperimentDfWrapper(df_growth, self.experiment_id, self.bioreplicate_ids)
        self.reads_data = ExperimentDfWrapper(df_reads, self.experiment_id, self.bioreplicate_ids)

        self.available_growth_measurements = [
            measurement
            for measurement in ['OD', 'Plate Counts', 'pH', 'FC']
            if measurement in df_growth.keys()
        ]

    def generate_growth_figures(self, measurement, args):
        selected_bioreplicate_ids = self.extract_args(args)
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

    def generate_reads_figures(self, args):
        selected_bioreplicate_ids = self.extract_args(args)
        self.reads_data.select_bioreplicates(selected_bioreplicate_ids)

        figs = []
        for bioreplicate_id, bioreplicate_df in self.reads_data.bioreplicate_dfs():
            species_columns = bioreplicate_df.filter(like='_counts').columns

            melted_df = bioreplicate_df.melt(
                id_vars=['Time', 'Biological_Replicate_id'],
                value_vars=species_columns,
                var_name='Species',
                value_name='Cells/mL'
            )

            figs.append(px.line(
                melted_df,
                x='Time',
                y='Cells/mL',
                color='Species',
                title=f'FC Counts: {bioreplicate_id} per Microbial Strain',
                labels={'Time': 'Hours'},
                template=PLOTLY_TEMPLATE,
                markers=True
            ))

        return figs

    def generate_metabolite_figures(self, args):
        selected_bioreplicate_ids = self.extract_args(args)
        self.growth_data.select_bioreplicates(selected_bioreplicate_ids)

        non_metabolite_keys = set([
            'Position', 'Biological_Replicate_id', 'Time',
            'OD', 'Plate Counts', 'pH', 'FC',
        ])
        metabolite_keys = set(self.growth_data.keys()).difference(non_metabolite_keys)

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

        for arg in args:
            if arg.endswith(':_average'):
                include_average = True
            elif arg.startswith('bioreplicate:'):
                selected_bioreplicate_ids.append(arg[len('bioreplicate:'):])

        if include_average:
            selected_bioreplicate_ids.append(f"Average {self.experiment_id}")

        return selected_bioreplicate_ids
