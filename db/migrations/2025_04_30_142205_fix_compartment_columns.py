import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Compartments
        CHANGE compartmentUniqueId id INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Compartments
        CHANGE compartmentId name varchar(50) COLLATE utf8mb4_bin NOT NULL,
        MODIFY volume DECIMAL(7,2),
        MODIFY pressure DECIMAL(7,2),
        CHANGE stirring_speed stirringSpeed FLOAT(7,2),
        CHANGE stirring_mode stirringMode varchar(50) COLLATE utf8mb4_bin,
        MODIFY O2 DECIMAL(7,2),
        MODIFY CO2 DECIMAL(7,2),
        MODIFY H2 DECIMAL(7,2),
        MODIFY N2 DECIMAL(7,2),
        MODIFY inoculumConcentration DECIMAL(20,3),
        MODIFY inoculumVolume DECIMAL(7,2),
        MODIFY initialPh DECIMAL(7,2),
        MODIFY initialTemperature DECIMAL(7,2),
        MODIFY carbonSource tinyint(1) DEFAULT '0',
        CHANGE mediaNames mediumName varchar(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE mediaLink mediumUrl varchar(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Compartments
        CHANGE id compartmentUniqueId INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Compartments
        CHANGE name compartmentId varchar(50) COLLATE utf8mb4_bin NOT NULL,
        MODIFY volume FLOAT(7,2) DEFAULT '0.00',
        MODIFY pressure FLOAT(7,2) DEFAULT '0.00',
        CHANGE stirringSpeed stirring_speed FLOAT(7,2) DEFAULT '0.00',
        CHANGE stirringMode stirring_mode varchar(50) COLLATE utf8mb4_bin DEFAULT '',
        MODIFY O2 float(7,2) DEFAULT '0.00',
        MODIFY CO2 float(7,2) DEFAULT '0.00',
        MODIFY H2 float(7,2) DEFAULT '0.00',
        MODIFY N2 float(7,2) DEFAULT '0.00',
        MODIFY inoculumConcentration float(10,2) DEFAULT '0.00',
        MODIFY inoculumVolume float(7,2) DEFAULT '0.00',
        MODIFY initialPh float(7,2) DEFAULT '0.00',
        MODIFY initialTemperature float(7,2) DEFAULT '0.00',
        MODIFY carbonSource tinyint(1) DEFAULT '0',
        CHANGE mediumName mediaNames varchar(100) COLLATE utf8mb4_bin NOT NULL,
        CHANGE mediumUrl mediaLink varchar(100) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
