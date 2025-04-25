import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE CalculationTechniques (
          id   INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          type VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,

          studyUniqueId VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,

          jobUuid VARCHAR(100) COLLATE utf8mb4_bin,
          state   VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,

          createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,

          CONSTRAINT CalculationTechniques_studyUniqueId FOREIGN KEY (studyUniqueId)
              REFERENCES Study (studyUniqueId)
              ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE CalculationTechniques;"))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
