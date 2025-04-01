import sqlalchemy as sql


def up(conn):
    conn.execute(sql.text("ALTER TABLE Measurements ADD COLUMN techniqueId INT"))
    conn.execute(sql.text("ALTER TABLE Measurements DROP COLUMN technique"))


def down(conn):
    conn.execute(sql.text("ALTER TABLE Measurements DROP COLUMN techniqueId"))
    conn.execute(sql.text(f"ALTER TABLE Measurements ADD COLUMN technique VARCHAR(100)"))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
