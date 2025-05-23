from datetime import datetime, UTC

import sqlalchemy as sql


def up(conn):
    queries = [
        "ALTER TABLE Study ADD COLUMN publishableAt    datetime",
        "ALTER TABLE Study ADD COLUMN publishedAt      datetime",
        "ALTER TABLE Study ADD COLUMN embargoExpiresAt datetime",
    ]

    for query in queries:
        conn.execute(sql.text(query))

    # Set existing timestamps
    query = """
        UPDATE Study
        SET
            publishableAt = :time,
            publishedAt = :time
    """
    conn.execute(sql.text(query), {
        'time': datetime.now(UTC),
    })


def down(conn):
    queries = [
        "ALTER TABLE Study DROP COLUMN publishableAt",
        "ALTER TABLE Study DROP COLUMN publishedAt",
        "ALTER TABLE Study DROP COLUMN embargoExpiresAt",
    ]

    for query in queries:
        conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
