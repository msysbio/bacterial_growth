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
        self.test_config = config['test']

        self.db = mysql.connector.connect(**self.test_config, use_pure=False)

        # Clean up database state before each test:
        with self.db.cursor() as conn:
            conn.execute('SHOW TABLES')
            tables = [t for (t,) in conn]
            for table in tables:
                conn.execute(f'DELETE FROM {table}')

    def tearDown(self):
        self.db.close()

    def create_streamlit_connection(self):
        import streamlit as st

        username = self.test_config['username']
        password = self.test_config['password']
        host     = self.test_config['host']
        port     = self.test_config['port']
        database = self.test_config['database']

        other = ''
        if 'unix_socket' in self.test_config:
            other += f"?unix_socket={self.test_config['unix_socket']}"

        st_url = f"mysql://{username}:{password}@{host}:{port}/{database}{other}"

        return st.connection("sql", url=st_url)
