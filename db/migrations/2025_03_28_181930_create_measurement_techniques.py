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
          studyUniqueId VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          metaboliteIds JSON DEFAULT (JSON_ARRAY()),
          strainIds     JSON DEFAULT (JSON_ARRAY()),

          createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          CONSTRAINT MeasurementTechniques_studyUniqueId FOREIGN KEY (studyUniqueId)
              REFERENCES Study (studyUniqueId)
              ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE MeasurementTechniques;"))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
