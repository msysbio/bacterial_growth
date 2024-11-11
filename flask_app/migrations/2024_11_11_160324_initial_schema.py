import os
from pathlib import Path

def up(conn):
    initial_schema_file = Path(os.path.dirname(__file__)) / '000_initial_schema.sql'
    initial_schema = initial_schema_file.read_text()

    for statement in initial_schema.split(';'):
        statement = statement.strip()
        if len(statement) > 0:
            conn.execute(sql.text(statement))

def down(conn):
    conn.execute(sql.text("""
        DROP TABLE Project;
        DROP TABLE Study;
        DROP TABLE Experiments;
        DROP TABLE Compartments;
        DROP TABLE Strains;
        DROP TABLE Community;
        DROP TABLE Metabolites;
        DROP TABLE Taxa;
        DROP TABLE MetaboliteSynonym;
        DROP TABLE CompartmentsPerExperiment;
        DROP TABLE TechniquesPerExperiment;
        DROP TABLE BioReplicatesPerExperiment;
        DROP TABLE BioReplicatesMetadata;
        DROP TABLE Perturbation;
        DROP TABLE MetabolitePerExperiment;
        DROP TABLE Abundances;
        DROP TABLE FC_Counts;
    """))

if __name__ == "__main__":
    from flask_app.lib.migrations import run
    run(__file__)
