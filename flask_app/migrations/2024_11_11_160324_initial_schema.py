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
    import sqlalchemy as sql
    from flask_app.db import get_connection

    with get_connection() as conn:
        # Bootstrap first migration
        conn.execute(sql.text("""
            CREATE TABLE IF NOT EXISTS MigrationVersions (
                id         BIGINT AUTO_INCREMENT,
                name       VARCHAR(255),
                migratedAt DATETIME DEFAULT CURRENT_TIMESTAMP,

                PRIMARY KEY (id)
            );
        """))
        conn.commit()

        migration_name = Path(__file__).stem
        migrated_at = conn.execute(
            sql.text('SELECT migratedAt FROM MigrationVersions WHERE name = :name'),
            { 'name': migration_name },
        ).scalar()

        if migrated_at is not None:
            print(f"> Skipping migration {migration_name}, run at {migrated_at}")
        else:
            up(conn)
            conn.execute(
                sql.text("INSERT INTO MigrationVersions (name) VALUES (:name)"),
                {'name': migration_name},
            )
            conn.commit()
