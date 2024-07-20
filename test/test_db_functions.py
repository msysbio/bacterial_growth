import unittest
import tomllib
from pathlib import Path

import mysql.connector

class TestDbFunctions(unittest.TestCase):
    def setUp(self):
        config      = tomllib.loads(Path('config/database.toml').read_text())
        test_config = config['test']

        self.db = mysql.connector.connect(**test_config, use_pure=False)

    def tearDown(self):
        self.db.close()

    def test_example(self):
        with self.db.cursor() as conn:
            conn.execute('select count(*) from Study')
            result = conn.fetchone()
            print(result)


if __name__ == '__main__':
    unittest.main()
