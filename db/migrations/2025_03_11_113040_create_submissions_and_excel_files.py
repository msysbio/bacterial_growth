import sqlalchemy as sql


def up(conn):
    query = """
        CREATE TABLE ExcelFiles (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

            filename VARCHAR(255),
            size     INT NOT NULL,
            content  LONGBLOB NOT NULL,

            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
        );
    """
    conn.execute(sql.text(query))

    query = """
        CREATE TABLE Submissions (
            id INT NOT NULL AUTO_INCREMENT PRIMARY KEY,

            projectUniqueID VARCHAR(100) COLLATE utf8mb4_bin,
            studyUniqueID   VARCHAR(100) COLLATE utf8mb4_bin,
            userUniqueID    VARCHAR(100) COLLATE utf8mb4_bin,

            studyDesign JSON DEFAULT (JSON_OBJECT()),

            studyFileId INT,
            dataFileId INT,

            createdAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
            updatedAt DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
        );
    """
    conn.execute(sql.text(query))


def down(conn):
    conn.execute(sql.text("DROP TABLE Submissions;"))
    conn.execute(sql.text("DROP TABLE ExcelFiles;"))


if __name__ == "__main__":
    from app.model.lib.migrate import run
    run(__file__, up, down)
