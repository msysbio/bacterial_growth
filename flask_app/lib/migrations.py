import sys
import subprocess
from pathlib import Path

import sqlalchemy as sql

from flask_app.db import get_connection, get_config

def run(file, up, down):
    migration_name = Path(file).stem
    direction = sys.argv[1] if len(sys.argv) > 1 else "up"

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

    # Dump database snapshot into flask_app/schema.sql
    schema_path = 'flask_app/schema.sql'
    db_config = get_config()

    with open(schema_path, 'w') as f:
        print(f"> Dumping schema in {schema_path}...")
        subprocess.run([
            '/usr/bin/mysqldump',
            '--no-data',
            f'-h{db_config["host"]}',
            f'-u{db_config["username"]}',
            f'-p{db_config["password"]}',
            db_config['database']
        ], stdout=f, stderr=subprocess.DEVNULL)
