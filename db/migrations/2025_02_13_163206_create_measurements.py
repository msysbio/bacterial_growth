import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Measurements (
            id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
            bioreplicateUniqueId int NOT NULL,
            position VARCHAR(100) NOT NULL,
            timeInSeconds int NOT NULL,
            pH VARCHAR(100) NOT NULL,
            unit VARCHAR(100) NOT NULL,
            technique VARCHAR(100) NOT NULL,
            absoluteValue DECIMAL(20, 2),
            relativeValue DECIMAL(10, 9),
            subjectType VARCHAR(100) NOT NULL,
            subjectId VARCHAR(100) NOT NULL,

            CONSTRAINT bioreplicateUniqueId FOREIGN KEY (bioreplicateUniqueId)
                REFERENCES BioReplicatesPerExperiment (bioreplicateUniqueId) ON DELETE CASCADE ON UPDATE CASCADE
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
