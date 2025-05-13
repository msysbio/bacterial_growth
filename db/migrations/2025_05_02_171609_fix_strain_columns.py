import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Strains
        CHANGE strainId id INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Strains
        CHANGE descriptionMember description TEXT,
        CHANGE memberName name VARCHAR(100) NOT NULL,
        DROP memberId
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Strains
        CHANGE id strainId INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Strains
        CHANGE description descriptionMember text COLLATE utf8mb4_bin,
        CHANGE name memberName TEXT COLLATE utf8mb4_bin,
        ADD memberId varchar(50) COLLATE utf8mb4_bin DEFAULT NULL
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
