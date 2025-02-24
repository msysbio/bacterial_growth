import sys
import subprocess
import os
import re
from pathlib import Path
import sqlalchemy as sql

from db import get_connection, get_config


def run(file, up, down, direction=None):
    """
    Run a migration

    Inputs
    ------
    file:      The filename of the migration, will be stored in the database after running
    up:        The function to execute to apply the migration
    down:      The function that reverts the migration
    direction: "up" or "down", taken from command-line arguments if not provided, defaults to "up"
    """
    migration_name = Path(file).stem
    if direction is None:
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
