import sqlalchemy as sql


def up(conn):
    print("")
    print("This migration deletes calculations/models, you need to regenerate them")
    print("")
    conn.execute(sql.text("DELETE FROM Calculations"))
    conn.execute(sql.text("DELETE FROM CalculationTechniques"))

    conn.execute(sql.text("RENAME TABLE CalculationTechniques to ModelingRequests"))
    conn.execute(sql.text("RENAME TABLE Calculations to ModelingResults"))

    query = """
        ALTER TABLE ModelingRequests
        DROP CONSTRAINT CalculationTechniques_studyUniqueId,
        DROP studyUniqueId,
        ADD studyId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD CONSTRAINT ModelingRequests_studyId
            FOREIGN KEY (studyId)
            REFERENCES Study (studyId)
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingResults
        CHANGE calculationTechniqueId requestId int NOT NULL,
        DROP CONSTRAINT Calculations_measurementTechniqueId,
        DROP measurementTechniqueId,
        DROP bioreplicateUniqueId,
        DROP subjectId,
        DROP subjectType
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingResults
        MODIFY error TEXT DEFAULT NULL,
        ADD fit JSON DEFAULT (json_object()),
        ADD measurementContextId INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    print("")
    print("This migration deletes calculations/models, you need to regenerate them")
    print("")
    conn.execute(sql.text("DELETE FROM ModelingRequests"))
    conn.execute(sql.text("DELETE FROM ModelingResults"))

    query = """
        ALTER TABLE ModelingResults
        MODIFY error VARCHAR(100) CHARACTER SET utf8mb4 COLLATE utf8mb4_bin DEFAULT NULL,
        DROP fit,
        DROP measurementContextId
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingResults
        CHANGE requestId calculationTechniqueId int NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingResults
        ADD measurementTechniqueId INT NOT NULL,
        ADD bioreplicateUniqueId int NOT NULL,
        ADD subjectId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD subjectType varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD CONSTRAINT Calculations_measurementTechniqueId
            FOREIGN KEY (measurementTechniqueId)
            REFERENCES MeasurementTechniques (id)
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE ModelingRequests
        DROP CONSTRAINT ModelingRequests_studyId,
        DROP studyId,
        ADD studyUniqueId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD CONSTRAINT CalculationTechniques_studyUniqueId
            FOREIGN KEY (studyUniqueId)
            REFERENCES Study (studyUniqueID)
        ;
    """
    conn.execute(sql.text(query))

    conn.execute(sql.text("RENAME TABLE ModelingRequests to CalculationTechniques"))
    conn.execute(sql.text("RENAME TABLE ModelingResults to Calculations"))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
