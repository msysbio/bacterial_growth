"""
Search for studies based on name, used metabolites, microbial strains, and
other criteria.
"""

from flask import render_template
import sqlalchemy as sql
import pandas as pd

from flask_app.db import get_connection
from flask_app.forms.search_form import SearchForm

from src.db_functions import dynamical_query

# TODO (2024-08-20) Use SQLalchemy model instead


def search_index_page():
    form = SearchForm()

    if form.validate_on_submit():
        query = dynamical_query([{ 'option': form.option.data, 'value': form.value.data }])

        with get_connection() as conn:
            studyIds = [studyId for (studyId,) in conn.execute(sql.text(query))]

            if len(studyIds) == 0:
                message = "Couldn't find a study with these parameters."
                return render_template("pages/search/index.html", form=form, error=message)

            results = []
            for studyId in studyIds:
                result = get_general_info(studyId, conn)

                result['experiments']               = get_experiments(studyId, conn)
                result['compartments']              = get_compartments(studyId, conn)
                result['communities']               = get_communities(studyId, conn)
                result['microbial_strains']         = get_microbial_strains(studyId, conn)
                result['biological_replicates']     = get_biological_replicates(studyId, conn)
                result['abundances']                = get_abundances(studyId, conn)
                result['fc_counts']                 = get_fc_counts(studyId, conn)
                result['metabolites_per_replicate'] = get_metabolites_per_replicate(studyId, conn)

                results.append(result)

            return render_template(
                "pages/search/index.html",
                form=form,
                results=results,
            )

    return render_template("pages/search/index.html", form=form)



def get_general_info(studyId, conn):
    params = { 'studyId': studyId }

    query = """
        SELECT studyId, studyName, studyDescription, studyURL
        FROM Study
        WHERE studyId = :studyId
    """
    result = conn.execute(sql.text(query), params).one()._asdict()

    query = """
        SELECT memberName, NCBId
        FROM Strains
        WHERE studyId = :studyId
        ORDER BY memberName ASC
    """
    result['members'] = list(conn.execute(sql.text(query), params).all())

    query = """
        SELECT DISTINCT technique
        FROM TechniquesPerExperiment
        WHERE studyId = :studyId
        ORDER BY technique ASC
    """
    result['techniques'] = list(conn.execute(sql.text(query), params).scalars())

    query = """
        SELECT DISTINCT metabo_name, cheb_id
        FROM MetabolitePerExperiment
        WHERE studyId = :studyId
        ORDER BY metabo_name ASC
    """
    result['metabolites'] = list(conn.execute(sql.text(query), params).all())

    return result


def get_experiments(studyId, conn):
    query = """
    SELECT
        E.experimentUniqueId,
        E.experimentId,
        E.experimentDescription,
        E.cultivationMode,
        GROUP_CONCAT(DISTINCT BRI.bioreplicateId) AS bioreplicateIds,
        E.controlDescription,
        GROUP_CONCAT(DISTINCT BR.bioreplicateId) AS control_bioreplicateIds,
        GROUP_CONCAT(DISTINCT C.comunityId) AS comunityIds,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM
        Experiments AS E
    LEFT JOIN
        BioReplicatesPerExperiment AS BRI ON E.experimentUniqueId = BRI.experimentUniqueId
    LEFT JOIN
        BioReplicatesPerExperiment AS BR ON E.experimentUniqueId = BR.experimentUniqueId
    LEFT JOIN
        Community AS C ON E.studyId = C.studyId
    LEFT JOIN
        CompartmentsPerExperiment AS CP ON E.experimentUniqueId = CP.experimentUniqueId
    WHERE
        E.studyId = %(studyId)s
        AND BR.controls = 1
    GROUP BY
        E.experimentId,
        E.experimentUniqueId,
        E.experimentDescription,
        E.cultivationMode,
        E.controlDescription;
    """
    df_experiments = pd.read_sql(query, conn, params={ 'studyId': studyId })
    columns_to_exclude = ['experimentUniqueId']
    return df_experiments.drop(columns=columns_to_exclude)


def get_compartments(studyId, conn):
    query = "SELECT DISTINCT * FROM Compartments WHERE studyId = %(studyId)s;"
    df_compartments = pd.read_sql(query, conn, params={ 'studyId': studyId })
    columns_to_exclude = ['studyId','compartmentUniqueId']
    return df_compartments.drop(columns=columns_to_exclude)


def get_communities(studyId, conn):
    query = """
    SELECT
        C.comunityId,
        GROUP_CONCAT(DISTINCT S.memberName) AS memberNames,
        GROUP_CONCAT(DISTINCT CP.compartmentId) AS compartmentIds
    FROM
        Community AS C
    LEFT JOIN
        Strains AS S ON C.strainId = S.strainId
    LEFT JOIN
        CompartmentsPerExperiment AS CP ON CP.comunityUniqueId = C.comunityUniqueId
    WHERE
        C.studyId = %(studyId)s
    GROUP BY
        C.comunityId;
    """
    df_communities = pd.read_sql(query, conn, params={ 'studyId': studyId })
    return df_communities


def get_microbial_strains(studyId, conn):
    query = "SELECT * FROM Strains WHERE studyId = %(studyId)s;"
    df_strains = pd.read_sql(query, conn, params={ 'studyId': studyId })
    columns_to_exclude = ['studyId']
    return df_strains.drop(columns=columns_to_exclude)


def get_biological_replicates(studyId, conn):
    query = """
    SELECT
        B.bioreplicateId,
        B.bioreplicateUniqueId,
        B.controls,
        B.OD,
        B.Plate_counts,
        B.pH,
        BM.biosampleLink,
        BM.bioreplicateDescrition
    FROM
        BioReplicatesPerExperiment AS B
    LEFT JOIN
        BioReplicatesMetadata AS BM ON B.bioreplicateUniqueId = BM.bioreplicateUniqueId
    WHERE
        B.studyId = %(studyId)s;
        """
    df_bioreps = pd.read_sql(query, conn, params={ 'studyId': studyId })
    columns_to_exclude = ['bioreplicateUniqueId']
    return df_bioreps.drop(columns=columns_to_exclude)

def get_abundances(studyId, conn):
    query = """
    SELECT
        A.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        Abundances AS A
    JOIN
        Strains AS S ON A.strainId = S.strainId
    WHERE
        A.studyId = %(studyId)s;
        """
    df_abundances = pd.read_sql(query, conn, params={ 'studyId': studyId })
    return df_abundances


def get_fc_counts(studyId, conn):
    query = """
    SELECT
        F.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        FC_Counts AS F
    JOIN
        Strains AS S ON F.strainId = S.strainId
    WHERE
        F.studyId = %(studyId)s;
        """
    df_fc_counts = pd.read_sql(query, conn, params={ 'studyId': studyId })
    return df_fc_counts


def get_metabolites_per_replicate(studyId, conn):
    query = "SELECT * FROM MetabolitePerExperiment WHERE studyId = %(studyId)s;"
    df_metabolites = pd.read_sql(query, conn, params={ 'studyId': studyId })
    columns_to_exclude = ['experimentUniqueId','experimentId','bioreplicateUniqueId']
    return df_metabolites.drop(columns=columns_to_exclude)
