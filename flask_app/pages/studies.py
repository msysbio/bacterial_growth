import os
import zipfile
from io import BytesIO

import pandas as pd
from flask import render_template, send_file

import flask_app.models.study_dfs as study_dfs
from flask_app.db import get_connection

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

def study_download_page(studyId):
    zip_file = createzip([studyId])

    return send_file(
        zip_file,
        as_attachment=True,
        download_name=f"{studyId}.zip",
    )


# TODO (2024-08-26) Hack, reads static files from the repo. Data needs to be
# stored in the database and rendered
def createzip(study_ids_list):
    buf = BytesIO()

    filepath = os.path.realpath(__file__)
    current_dir = os.path.dirname(filepath)
    root_dir = os.path.dirname(current_dir)
    relative_path_to_src = os.path.join(root_dir, '../src')

    with zipfile.ZipFile(buf, 'w', zipfile.ZIP_DEFLATED) as csv_zip:
        for study_id in study_ids_list:
            folder_path = relative_path_to_src + f"/Data/Growth/{study_id}"
            #st.info(folder_path)
            growth_file = folder_path + f"/Growth_Metabolites.csv"
            reads_file = folder_path + f"/Sequencing_Reads.csv"
            try:
                df_growth = pd.read_csv(growth_file)
            # Continue with processing the dataframe...
            except FileNotFoundError:
                # TODO (2024-08-26) Logging
                print(f"CSV file '{growth_file}' not found. Skipping...")
            df_growth = pd.read_csv(growth_file)
            df_reads = pd.read_csv(reads_file)
            if not df_growth.empty:
                csv_zip.writestr(f"{study_id}_Growth_Metabolites.csv", df_growth.to_csv())
            if not df_reads.empty:
                csv_zip.writestr(f"{study_id}_Sequencing_Reads.csv", df_reads.to_csv())

    buf.seek(0)
    return buf
