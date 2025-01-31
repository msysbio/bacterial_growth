import uuid

# Will be auto-incremented to create sequential database ids:
STUDY_ID = 0
PROJECT_UID = 0
CHEBI_ID = 0


def create_study(conn, **params):
    global STUDY_ID
    global PROJECT_UID

    STUDY_ID += 1
    PROJECT_UID += 1

    default_params = {
        'studyId':          str(STUDY_ID),
        'projectUniqueID':  str(PROJECT_UID),
        'studyName':        'Test study',
        'studyDescription': f'Test study description of {STUDY_ID}',
        'studyURL':         'https://example.org/study',
        'studyUniqueID':    str(uuid.uuid4())
    }

    params = {**default_params, **params}

    conn.execute("""
        INSERT INTO Study VALUES (
            %(studyId)s, %(projectUniqueID)s,
            %(studyName)s, %(studyDescription)s, %(studyURL)s, %(studyUniqueID)s
        )
    """, params)


def create_metabolite(conn, **params):
    global CHEBI_ID

    CHEBI_ID += 1
    chebi_id = f"Chebi_{CHEBI_ID}"

    default_params = {
        'chebi_id':     chebi_id,
        'metabo_name': "Test metabolite",
    }

    params = {**default_params, **params}

    conn.execute("""
        INSERT INTO Metabolites VALUES (%(chebi_id)s, %(metabo_name)s)
    """, params)

    return chebi_id
