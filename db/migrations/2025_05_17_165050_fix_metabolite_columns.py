import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Metabolites
        DROP PRIMARY KEY,
        ADD id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        ADD UNIQUE INDEX Metabolites_chebiId (chebi_id)
        ;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Metabolites
        CHANGE chebi_id chebiId varchar(512) COLLATE utf8mb4_bin NOT NULL,
        CHANGE metabo_name name varchar(512) NOT NULL,
        ADD COLUMN averageMass DECIMAL (10,5) DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Metabolites
        DROP PRIMARY KEY,
        DROP id,
        DROP INDEX Metabolites_chebiId,
        ADD PRIMARY KEY (chebiId)
        ;

    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Metabolites
        CHANGE chebiId chebi_id varchar(512) COLLATE utf8mb4_bin NOT NULL,
        CHANGE name metabo_name varchar(512) DEFAULT NULL,
        DROP averageMass
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
