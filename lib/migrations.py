import sys
import subprocess
import re
from pathlib import Path

import sqlalchemy as sql

from db import get_connection, get_config

# TODO (2025-02-04) Reset test db with the schema.sql file. Problem: studyId is
# DEFAULT NULL in some cases.

def run(file, up, down):
    migration_name = Path(file).stem
    direction = sys.argv[1] if len(sys.argv) > 1 else "up"

    with get_connection() as conn:
        migrated_at = conn.execute(
            sql.text('SELECT migratedAt FROM MigrationVersions WHERE name = :name'),
            { 'name': migration_name },
        ).scalar()

        if direction == "up":
            if migrated_at is None:
                print(f"> Migrating {migration_name}...")
                up(conn)
                conn.execute(
                    sql.text("INSERT INTO MigrationVersions (name) VALUES (:name)"),
                    {'name': migration_name},
                )
                conn.commit()
            else:
                print(f"> Skipping migration {migration_name}, run at {migrated_at}")
        elif direction == "down":
            if migrated_at is None:
                print(f"> Skipping {migration_name}, not run")
            else:
                print(f"> Rolling back {migration_name}...")
                down(conn)
                conn.execute(
                    sql.text("DELETE FROM MigrationVersions WHERE name = :name"),
                    {'name': migration_name},
                )
                conn.commit()
        else:
            raise ValueError(f"Unknown migration direction: {direction}")

    # Dump database snapshot into schema.sql
    schema_path = 'db/schema.sql'
    db_config = get_config()

    with open(schema_path, 'w') as f:
        print(f"> Dumping schema in {schema_path}...")

        schema_output = subprocess.run([
            '/usr/bin/mysqldump',
            '--no-data',
            '--skip-quote-names',
            f'-h{db_config["host"]}',
            f'-u{db_config["username"]}',
            f'-p{db_config["password"]}',
            db_config['database'],
        ], capture_output=True).stdout.decode('utf-8')

        # Remove auto increment snapshots
        schema_output = re.sub(r' AUTO_INCREMENT=[0-9]*\b', '', schema_output)

        migration_version_data = subprocess.run([
            '/usr/bin/mysqldump',
            '--no-create-info',
            '--skip-quote-names',
            '--compact',
            f'-h{db_config["host"]}',
            f'-u{db_config["username"]}',
            f'-p{db_config["password"]}',
            db_config['database'],
            'MigrationVersions',
        ], capture_output=True).stdout.decode('utf-8')

        schema_output = re.sub(r'(-- Dump completed)', f"{migration_version_data}\n\\1", schema_output)

        Path(schema_path).write_text(schema_output)
