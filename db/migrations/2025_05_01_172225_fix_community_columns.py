import sqlalchemy as sql


def up(conn):
    query = "RENAME TABLE Community to Communities"
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Communities
        CHANGE communityUniqueId id INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Communities
        CHANGE communityId name varchar(100) COLLATE utf8mb4_bin NOT NULL,
        DROP CONSTRAINT Community_fk_1,
        DROP CONSTRAINT communityId,
        DROP strainId,
        ADD strainIds JSON NOT NULL DEFAULT (JSON_ARRAY())
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Communities
        CHANGE id communityUniqueId INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Communities
        CHANGE name communityId varchar(100) COLLATE utf8mb4_bin NOT NULL,
        ADD strainId INT DEFAULT NULL,
        ADD CONSTRAINT Community_fk_1
            FOREIGN KEY (strainId)
            REFERENCES Strains (strainId)
            ON DELETE CASCADE ON UPDATE CASCADE,
        ADD CONSTRAINT UNIQUE communityId (communityId,strainId),
        DROP strainIds
        ;
    """
    conn.execute(sql.text(query))

    query = "RENAME TABLE Communities to Community"
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
