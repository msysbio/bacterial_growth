import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE ProjectUsers (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

            projectUniqueID VARCHAR(100) COLLATE utf8mb4_bin,
            userUniqueID    VARCHAR(100) COLLATE utf8mb4_bin,

            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT projectUniqueID FOREIGN KEY (projectUniqueID)
                REFERENCES Project (projectUniqueID)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    conn.execute(sql.text(query))

    query = """
        CREATE TABLE StudyUsers (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

            studyUniqueID VARCHAR(100) COLLATE utf8mb4_bin,
            userUniqueID  VARCHAR(100) COLLATE utf8mb4_bin,

            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,

            CONSTRAINT studyUniqueID FOREIGN KEY (studyUniqueID)
                REFERENCES Study (studyUniqueID)
                ON DELETE CASCADE ON UPDATE CASCADE
        )
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE StudyUsers;"))
    conn.execute(sql.text("DROP TABLE ProjectUsers;"))


if __name__ == "__main__":
    from lib.migrate import run
    run(__file__, up, down)
