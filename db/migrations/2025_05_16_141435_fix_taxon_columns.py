import sqlalchemy as sql


def up(conn):
    query = """
        ALTER TABLE Taxa
        DROP PRIMARY KEY,
        ADD id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
        CHANGE tax_id ncbiId VARCHAR(50) COLLATE utf8mb4_bin NOT NULL,
        CHANGE tax_names name VARCHAR(512) NOT NULL,
        ADD UNIQUE INDEX Taxa_ncbiId (ncbiId)
        ;
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        ALTER TABLE Taxa
        DROP PRIMARY KEY,
        DROP id,
        CHANGE ncbiId tax_id VARCHAR(512) COLLATE utf8mb4_bin NOT NULL,
        CHANGE name tax_names VARCHAR(512) COLLATE utf8mb4_bin NOT NULL,
        ADD PRIMARY KEY (tax_id),
        DROP KEY Taxa_ncbiId
        ;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
