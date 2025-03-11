import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE Submissions (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

            projectUniqueID VARCHAR(100) COLLATE utf8mb4_bin,
            studyUniqueID   VARCHAR(100) COLLATE utf8mb4_bin,
            userUniqueID    VARCHAR(100) COLLATE utf8mb4_bin,

            studyDesign JSON DEFAULT (JSON_OBJECT())
        );
    """
    params = {}

    conn.execute(sql.text(query), params)


def down(conn):
    query = """
        DROP TABLE Submissions;
    """
    conn.execute(sql.text(query))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
