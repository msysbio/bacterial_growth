import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE MeasurementTechniques (
          id            INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          type          VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          subjectType   VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          units         VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          description   TEXT,
          includeStd    tinyint(1) NOT NULL DEFAULT '0',
          studyId       VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          metaboliteIds JSON DEFAULT (JSON_ARRAY()),

          createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          CONSTRAINT MeasurementTechniques_studyId FOREIGN KEY (studyId)
              REFERENCES Study (studyId)
              ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE MeasurementTechniques;"))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
