import os
import unittest
import tomllib
from pathlib import Path

import mysql.connector


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        assert(os.environ['APP_ENV'] == 'test')

        # Connect to the test database:
        config = tomllib.loads(Path('config/database.toml').read_text())
        self.db = mysql.connector.connect(**config['test'], use_pure=False)

        # Clean up database state before each test:
        with self.db.cursor() as conn:
            conn.execute('SHOW TABLES')
            tables = [t for (t,) in conn]
            for table in tables:
                conn.execute(f'DELETE FROM {table}')

    def tearDown(self):
        self.db.close()
