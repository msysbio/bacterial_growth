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
                result['experiments'] = get_experiments(studyId, conn)

                results.append(result)

            return render_template(
                "pages/search/index.html",
                form=form,
                results=results,
            )

    return render_template("pages/search/index.html", form=form)



def get_general_info(studyId, conn):
    params = { 'studyId': studyId }

    query = f"""
        SELECT studyId, studyName, studyDescription, studyURL
        FROM Study
        WHERE studyId = :studyId
    """
    result = conn.execute(sql.text(query), params).one()._asdict()

    query = f"""
        SELECT memberName, NCBId
        FROM Strains
        WHERE studyId = :studyId
        ORDER BY memberName ASC
    """
    result['members'] = list(conn.execute(sql.text(query), params).all())

    query = f"""
        SELECT DISTINCT technique
        FROM TechniquesPerExperiment
        WHERE studyId = :studyId
        ORDER BY technique ASC
    """
    result['techniques'] = list(conn.execute(sql.text(query), params).scalars())

    query = f"""
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


def get_compartments(studyID, conn):
    query = f"SELECT DISTINCT * FROM Compartments WHERE studyId = '{studyID}';"
    df_Compartment = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId','compartmentUniqueId']
    return df_Compartment.drop(columns=columns_to_exclude)


def get_communities(studyID, conn):
    query = f"""
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
        C.studyId = '{studyID}'
    GROUP BY
        C.comunityId;
    """
    df_communities = conn.query(query, ttl=600)
    #columns_to_exclude = ['studyId', 'perturbationUniqueId']
    return df_communities


def get_microbial_strains(studyID, conn):
    query = f"SELECT * FROM Strains WHERE studyId = '{studyID}';"
    df_Bacteria = conn.query(query, ttl=600)
    columns_to_exclude = ['studyId']
    return df_Bacteria.drop(columns=columns_to_exclude)


def get_biological_replicates(studyID, conn):
    query = f"""
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
        B.studyId = '{studyID}';
        """
    df_bioreps = conn.query(query, ttl=600)
    columns_to_exclude = ['bioreplicateUniqueId']
    return df_bioreps.drop(columns=columns_to_exclude)

def get_abundances(studyID, conn):
    query = f"""
    SELECT
        A.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        Abundances AS A
    JOIN
        Strains AS S ON A.strainId = S.strainId
    WHERE
        A.studyId = '{studyID}';
        """
    df_abundances = conn.query(query, ttl=600)
    return df_abundances


def get_fc_counts(studyID, conn):
    query = f"""
    SELECT
        F.bioreplicateId,
        S.memberName,
        S.NCBId
    FROM
        FC_Counts AS F
    JOIN
        Strains AS S ON F.strainId = S.strainId
    WHERE
        F.studyId = '{studyID}';
        """
    df_FC = conn.query(query, ttl=600)
    return df_FC
