import sqlalchemy as sql


def up(conn):
    print("")
    print("[Warning] This migration deletes measurements, they need to be regenerated")
    print("")
    conn.execute(sql.text("DELETE FROM Measurements"))

    query = """
        ALTER TABLE Measurements

        DROP CONSTRAINT bioreplicateUniqueId,
        DROP CONSTRAINT studyId,
        DROP CONSTRAINT Measurements_fk_1,

        DROP bioreplicateUniqueId,
        DROP pH,
        DROP unit,
        DROP technique,
        DROP subjectType,
        DROP subjectId,
        DROP techniqueId,
        DROP compartmentId
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Measurements
        ADD contextId int NOT NULL,

        ADD CONSTRAINT Measurements_fk_1
            FOREIGN KEY (contextId)
            REFERENCES MeasurementContexts (id)
            ON DELETE CASCADE ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    print("")
    print("[Warning] This migration deletes measurements, they need to be regenerated")
    print("")
    conn.execute(sql.text("DELETE FROM Measurements"))

    query = """
        ALTER TABLE Measurements
        DROP contextId,
        DROP CONSTRAINT Measurements_fk_1
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Measurements
        ADD bioreplicateUniqueId int NOT NULL,
        ADD pH varchar(100) DEFAULT NULL,
        ADD unit varchar(100) DEFAULT NULL,
        ADD technique varchar(100) DEFAULT NULL,
        ADD subjectType varchar(100) NOT NULL,
        ADD subjectId varchar(100) NOT NULL,
        ADD techniqueId int DEFAULT NULL,
        ADD compartmentId int NOT NULL,

        ADD CONSTRAINT bioreplicateUniqueId
            FOREIGN KEY (bioreplicateUniqueId)
            REFERENCES Bioreplicates (id)
            ON DELETE CASCADE ON UPDATE CASCADE,

        ADD CONSTRAINT Measurements_fk_1
            FOREIGN KEY (compartmentId)
            REFERENCES Compartments (id)
            ON DELETE CASCADE ON UPDATE CASCADE,

        ADD CONSTRAINT studyId
            FOREIGN KEY (studyId)
            REFERENCES Study (studyId)
            ON DELETE CASCADE ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
