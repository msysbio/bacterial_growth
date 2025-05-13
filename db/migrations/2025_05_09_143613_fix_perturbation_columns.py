import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Perturbation
        CHANGE perturbationUniqueid id INT NOT NULL AUTO_INCREMENT,
        CHANGE perturbationDescription description TEXT,

        DROP perturbationId,
        DROP experimentId,
        DROP perturbationMinimumValue,
        DROP perturbationMaximumValue,
        DROP perturbationStartTime,
        DROP perturbationEndTime,
        DROP OLDCompartmentId,
        DROP NEWCompartmentId,
        DROP OLDComunityId,
        DROP NEWComunityId,

        ADD removedCompartmentId int DEFAULT NULL,
        ADD addedCompartmentId int DEFAULT NULL,
        ADD oldCommunityId int DEFAULT NULL,
        ADD newCommunityId int DEFAULT NULL,
        ADD startTimepoint int NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Perturbation
        CHANGE experimentUniqueId experimentId INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = "RENAME TABLE Perturbation to Perturbations"
    conn.execute(sql.text(query))


def down(conn):
    query = "RENAME TABLE Perturbations to Perturbation"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Perturbation
        CHANGE experimentId experimentUniqueId INT NOT NULL
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Perturbation

        DROP startTimepoint,
        DROP newCommunityId,
        DROP oldCommunityId,
        DROP addedCompartmentId,
        DROP removedCompartmentId,

        ADD OLDCompartmentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD OLDComunityId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD NEWCompartmentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD NEWComunityId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD perturbationMinimumValue decimal(10,2) DEFAULT NULL,
        ADD perturbationMaximumValue decimal(10,2) DEFAULT NULL,
        ADD perturbationStartTime time DEFAULT NULL,
        ADD perturbationEndTime time DEFAULT NULL,
        ADD experimentId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,
        ADD perturbationId varchar(100) COLLATE utf8mb4_bin DEFAULT NULL,

        CHANGE description perturbationDescription TEXT,
        CHANGE id perturbationUniqueid INT NOT NULL AUTO_INCREMENT
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
