import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Users (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,
            uuid VARCHAR(100) NOT NULL,
            orcidId VARCHAR(100) NOT NULL,
            orcidToken VARCHAR(100) NOT NULL,
            name VARCHAR(255) NOT NULL,
            isAdmin tinyint(1) NOT NULL DEFAULT '0',
            createdAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
            lastLoginAt datetime NOT NULL DEFAULT CURRENT_TIMESTAMP,

            UNIQUE INDEX Users_uuid (uuid),
            UNIQUE INDEX Users_orcidId (orcidId)
        )
    """
    conn.execute(sql.text(query))


def down(conn):
    query = """
        DROP TABLE Users;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
