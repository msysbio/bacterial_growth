from flask import render_template

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
