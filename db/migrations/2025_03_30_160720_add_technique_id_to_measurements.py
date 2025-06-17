import sqlalchemy as sql


def up(conn):
    conn.execute(sql.text("ALTER TABLE Measurements ADD techniqueId INT"))
    conn.execute(sql.text("ALTER TABLE Measurements MODIFY technique varchar(100) DEFAULT NULL"))


def down(conn):
    conn.execute(sql.text("ALTER TABLE Measurements DROP COLUMN techniqueId"))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
