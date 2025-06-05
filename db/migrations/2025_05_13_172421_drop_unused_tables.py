import sqlalchemy as sql


def up(conn):
    conn.execute(sql.text("DROP TABLE Abundances;"))
    conn.execute(sql.text("DROP TABLE FC_Counts;"))
    conn.execute(sql.text("DROP TABLE TechniquesPerExperiment;"))


def down(conn):
    query = """
        CREATE TABLE Abundances (
            studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
            experimentUniqueId int NOT NULL,
            experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            bioreplicateUniqueId int NOT NULL,
            bioreplicateId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            strainId int DEFAULT NULL,
            memberId varchar(255) COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (experimentUniqueId,bioreplicateUniqueId,memberId),
            KEY fk_1 (experimentUniqueId),
            KEY fk_2 (strainId),
            KEY fk_3 (studyId),
            CONSTRAINT Abundances_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT Abundances_fk_2 FOREIGN KEY (strainId) REFERENCES Strains (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT Abundances_fk_3 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
    """
    conn.execute(sql.text(query))

    query = """
        CREATE TABLE FC_Counts (
            studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
            experimentUniqueId int DEFAULT NULL,
            experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            bioreplicateUniqueId int DEFAULT NULL,
            bioreplicateId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            strainId int DEFAULT NULL,
            memberId varchar(255) COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (experimentId,bioreplicateId,memberId),
            KEY fk_1 (experimentUniqueId),
            KEY fk_2 (strainId),
            KEY fk_3 (studyId),
            CONSTRAINT FC_Counts_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT FC_Counts_fk_2 FOREIGN KEY (strainId) REFERENCES Strains (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT FC_Counts_fk_3 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
    """
    conn.execute(sql.text(query))

    query = """
        CREATE TABLE TechniquesPerExperiment (
            studyId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
            experimentUniqueId int NOT NULL,
            experimentId varchar(100) COLLATE utf8mb4_bin NOT NULL,
            technique varchar(100) COLLATE utf8mb4_bin NOT NULL,
            techniqueUnit varchar(100) COLLATE utf8mb4_bin NOT NULL,
            PRIMARY KEY (experimentUniqueId,technique,techniqueUnit),
            KEY fk_2 (studyId),
            CONSTRAINT TechniquesPerExperiment_fk_1 FOREIGN KEY (experimentUniqueId) REFERENCES Experiments (id) ON DELETE CASCADE ON UPDATE CASCADE,
            CONSTRAINT TechniquesPerExperiment_fk_2 FOREIGN KEY (studyId) REFERENCES Study (studyId) ON DELETE CASCADE ON UPDATE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_bin;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
