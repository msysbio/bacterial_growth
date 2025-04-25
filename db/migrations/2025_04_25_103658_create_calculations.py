import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Calculations (
          id          INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
          type        VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          subjectId   VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          subjectType VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,

          calculationTechniqueId int NOT NULL,
          measurementTechniqueId int NOT NULL,

          coefficients JSON DEFAULT (JSON_OBJECT()),

          state VARCHAR(100) COLLATE utf8mb4_bin NOT NULL,
          error VARCHAR(100) COLLATE utf8mb4_bin,

          createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
          updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
          calculatedAt datetime,

          CONSTRAINT Calculations_measurementTechniqueId FOREIGN KEY (measurementTechniqueId)
              REFERENCES MeasurementTechniques (id)
              ON DELETE CASCADE ON UPDATE CASCADE,

          CONSTRAINT Calculations_calculationTechniqueId FOREIGN KEY (calculationTechniqueId)
              REFERENCES CalculationTechniques (id)
              ON DELETE CASCADE ON UPDATE CASCADE
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE Calculations;"))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
