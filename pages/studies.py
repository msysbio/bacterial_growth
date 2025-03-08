import zipfile
from io import BytesIO
import functools

from flask import render_template, send_file, request
import sqlalchemy as sql

import models.study_dfs as study_dfs
from models.study import Study
from models.experiment import Experiment
from models.bioreplicate import Bioreplicate
from models.measurement import Measurement

from db import get_connection, get_session
from lib.db import execute_into_df

# TODO (2025-03-08) Average bioreplicate
# TODO (2025-03-08) Extract to class
# TODO (2025-03-08) Counts, reads
# TODO (2025-03-08) Write tests


def study_show_page(studyId):
    with get_connection() as conn:
        study = study_dfs.get_general_info(studyId, conn)

        study['experiments']               = study_dfs.get_experiments(studyId, conn)
        study['compartments']              = study_dfs.get_compartments(studyId, conn)
        study['communities']               = study_dfs.get_communities(studyId, conn)
        study['microbial_strains']         = study_dfs.get_microbial_strains(studyId, conn)
        study['biological_replicates']     = study_dfs.get_biological_replicates(studyId, conn)
        study['abundances']                = study_dfs.get_abundances(studyId, conn)
        study['fc_counts']                 = study_dfs.get_fc_counts(studyId, conn)
        study['metabolites_per_replicate'] = study_dfs.get_metabolites_per_replicate(studyId, conn)

        return render_template("pages/studies/show.html", study=study)


def study_export_page(studyId):
    with get_session() as db_session:
        study = db_session.get(Study, studyId)

        return render_template(
            "pages/studies/export.html",
            study=study,
            studyId=studyId,
        )


def study_export_preview_fragment(studyId):
    sep = extract_csv_separator(request.args)

    with get_session() as db_session:
        csv_previews = []
        bioreplicate_uuids = request.args.getlist('bioreplicates')

        for experiment, experiment_df in get_experiment_data_for_export(studyId, db_session, bioreplicate_uuids):
            if len(experiment_df) == 0:
                continue

            csv = experiment_df[:5].to_csv(index=False, sep=sep)
            csv_previews.append(f"""
                <h3>{experiment.experimentId}.csv ({len(experiment_df)} rows)</h3>
                <pre>{csv}</pre>
            """)

        return '\n'.join(csv_previews)


def study_download_zip(studyId):
    sep = extract_csv_separator(request.args)

    with get_session() as db_session:
        csv_data = []
        bioreplicate_uuids = request.args.getlist('bioreplicates')
        experiments = []

        for experiment, experiment_df in get_experiment_data_for_export(studyId, db_session, bioreplicate_uuids):
            if len(experiment_df) == 0:
                continue

            csv_bytes = experiment_df.to_csv(index=False, sep=sep)
            csv_name = f"{experiment.experimentId}.csv"

            csv_data.append((csv_name, csv_bytes))
            experiments.append(experiment)

        study = study_dfs.get_general_info(studyId, db_session)
        readme_text = render_template('pages/studies/export_readme.md', study=study, experiments=experiments)

    zip_file = createzip(csv_data, readme_text)

    return send_file(
        zip_file,
        as_attachment=True,
        download_name=f"{studyId}.zip",
    )


def extract_csv_separator(args):
    delimiter = args.get('delimiter', 'comma')

    if delimiter == 'comma':
        sep = ','
    elif delimiter == 'tab':
        sep = '\t'
    elif delimiter == 'custom':
        sep = args.get('custom_delimiter', '|')
        if sep == '':
            sep = ' '
    else:
        raise Exception(f"Unknown delimiter requested: {delimiter}")

    return sep


def get_experiment_data_for_export(studyId, db_session, bioreplicate_uuids):
    experiments = db_session.scalars(
        sql.select(Experiment)
        .join(Bioreplicate)
        .where(Experiment.studyId == studyId)
        .where(Bioreplicate.bioreplicateUniqueId.in_(bioreplicate_uuids))
        .group_by(Experiment.experimentUniqueId)
    ).all()

    filtered_experiments = []
    get_subject = functools.cache(Measurement.get_subject)

    for experiment in experiments:
        measurement_dfs = []
        measurement_targets = {
            'bioreplicate': set(),
            'metabolite':   set(),
            'strain':       set(),
        }

        # Collect targets for each column of measurements:
        for bioreplicate in experiment.bioreplicates:
            for measurement in bioreplicate.measurements:
                if measurement.subjectType.value == 'bioreplicate':
                    measurement_targets['bioreplicate'].add((
                        measurement.technique,
                        measurement.unit,
                    ))
                else:
                    subject = get_subject(measurement.subjectId, measurement.subjectType.value)
                    measurement_targets[measurement.subjectType.value].add((
                        subject,
                        measurement.technique,
                        measurement.unit,
                    ))

        for (technique, unit) in measurement_targets['bioreplicate']:
            query = measurement_base_query(experiment, bioreplicate_uuids, f"{technique} ({unit})").where(
                Measurement.subjectType == 'bioreplicate',
                Measurement.technique == technique,
            )
            measurement_dfs.append(execute_into_df(db_session, query))

        for subject_type in ('strain', 'metabolite'):
            for (subject, technique, unit) in sorted(measurement_targets[subject_type]):
                query = measurement_base_query(experiment, bioreplicate_uuids, f"{subject.name} ({unit})").where(
                    Measurement.subjectType == subject_type,
                    Measurement.subjectId == subject.id,
                )
                measurement_dfs.append(execute_into_df(db_session, query))

        if len(measurement_dfs) == 0:
            continue

        # Join separate dataframes, one per column
        experiment_df = measurement_dfs[0]
        for df in measurement_dfs[1:]:
            experiment_df = experiment_df.merge(
                df,
                how='left',
                on=['Time (hours)', 'Biological Replicate ID'],
                validate='one_to_one',
                suffixes=(None, None),
            )

        filtered_experiments.append((experiment, experiment_df))

    return filtered_experiments


def measurement_base_query(experiment, bioreplicate_uuids, value_label):
    return (
        sql.select(
            Measurement.timeInHours.label("Time (hours)"),
            Bioreplicate.bioreplicateId.label("Biological Replicate ID"),
            Measurement.value.label(value_label),
        )
        .join(Bioreplicate)
        .join(Experiment)
        .where(
            Experiment.experimentUniqueId == experiment.experimentUniqueId,
            Bioreplicate.bioreplicateUniqueId.in_(bioreplicate_uuids),
        )
        .order_by(Bioreplicate.bioreplicateId, Measurement.timeInSeconds)
    )


def createzip(csv_data: list[tuple[str, bytes]], readme_text: str):
    buf = BytesIO()

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as csv_zip:
        for (csv_name, csv_bytes) in csv_data:
            csv_zip.writestr(csv_name, csv_bytes)

        csv_zip.writestr('README.md', readme_text)

    buf.seek(0)
    return buf
