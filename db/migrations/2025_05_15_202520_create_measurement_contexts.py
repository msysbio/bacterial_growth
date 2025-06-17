import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE MeasurementContexts(
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
            bioreplicateId int NOT NULL,
            compartmentId int NOT NULL,
            techniqueId int DEFAULT NULL,
            subjectId varchar(100) NOT NULL,
            subjectType varchar(100) NOT NULL,

            CONSTRAINT MeasurementContexts_fk_1
                FOREIGN KEY (bioreplicateId)
                REFERENCES Bioreplicates (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT MeasurementContexts_fk_2
                FOREIGN KEY (compartmentId)
                REFERENCES Compartments (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT MeasurementContexts_fk_3
                FOREIGN KEY (techniqueId)
                REFERENCES MeasurementTechniques (id)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT MeasurementContexts_fk_4
                FOREIGN KEY (studyId)
                REFERENCES Study (studyId)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE MeasurementContexts"))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
