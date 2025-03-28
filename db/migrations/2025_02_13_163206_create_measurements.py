import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Measurements (
            id                   INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            bioreplicateUniqueId INT NOT NULL,
            studyId              VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
            position             VARCHAR(100) NOT NULL,
            timeInSeconds        INT NOT NULL,
            pH                   VARCHAR(100),
            unit                 VARCHAR(100),
            technique            VARCHAR(100) NOT NULL,
            value                DECIMAL(20, 3),
            std                  DECIMAL(20, 3),
            subjectType          VARCHAR(100) NOT NULL,
            subjectId            VARCHAR(100) NOT NULL,

            CONSTRAINT bioreplicateUniqueId FOREIGN KEY (bioreplicateUniqueId)
                REFERENCES BioReplicatesPerExperiment (bioreplicateUniqueId)
                ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT studyId FOREIGN KEY (studyId)
                REFERENCES Study (studyId)
                ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        DROP TABLE Measurements;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
