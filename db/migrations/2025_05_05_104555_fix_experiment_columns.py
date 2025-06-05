import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Experiments
        CHANGE experimentUniqueId id INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Experiments
        CHANGE experimentDescription description TEXT,
        CHANGE experimentId name VARCHAR(100) NOT NULL,
        DROP controlDescription,
        ADD communityId INT,

        ADD CONSTRAINT Experiment_fk_1
            FOREIGN KEY (communityId)
            REFERENCES Communities (id)
            ON DELETE SET NULL ON UPDATE CASCADE
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Experiments
        CHANGE id experimentUniqueId INT NOT NULL AUTO_INCREMENT;
    """
    conn.execute(sql.text(query))

    query = """
        ALTER TABLE Experiments
        CHANGE description experimentDescription text COLLATE utf8mb4_bin,
        CHANGE name experimentId VARCHAR(100) COLLATE utf8mb4_bin,
        ADD controlDescription TEXT COLLATE utf8mb4_bin DEFAULT NULL,
        DROP CONSTRAINT Experiment_fk_1,
        DROP communityId
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
