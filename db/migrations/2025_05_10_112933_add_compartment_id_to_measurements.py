import sqlalchemy as sql


def up(conn):
    print("")
    print("[Warning] This migration deletes measurements, they need to be regenerated")
    print("")
    conn.execute(sql.text("DELETE FROM Measurements"))

    query = """
        ALTER TABLE Measurements
        ADD compartmentId int NOT NULL,
        ADD CONSTRAINT Measurements_fk_1
            FOREIGN KEY (compartmentId)
            REFERENCES Compartments (id)
            ON DELETE CASCADE ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Measurements
        DROP CONSTRAINT Measurements_fk_1,
        DROP compartmentId
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
