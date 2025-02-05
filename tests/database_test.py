import os
import unittest

import sqlalchemy as sql

import db

class DatabaseTest(unittest.TestCase):
    def setUp(self):
        assert os.environ['APP_ENV'] == 'test'

        self.db_conn = db.get_connection()

        # Clean up database state before each test:
        tables = self.db_conn.execute(sql.text('SHOW TABLES')).scalars().all()
        for table in tables:
            self.db_conn.execute(sql.text(f'DELETE FROM {table}'))

    def tearDown(self):
        self.db_conn.close()

    def simple_query(self, query, **params):
        results = self.db_conn.execute(sql.text(query), params).all()
        return [row._asdict() for row in results]

    def create_taxon(self, **params):
        self.taxa_id = getattr(self, 'taxa_id', 0) + 1
        params = {
            'tax_id': self.taxa_id,
            'tax_names': f"Taxon {self.taxa_id}",
            **params,
        }

        query = sql.text("INSERT INTO Taxa VALUES (:tax_id, :tax_names)")
        self.db_conn.execute(query, params)

        return params

    def create_metabolite(self, **params):
        self.metabolite_id = getattr(self, 'metabolite_id', 0) + 1
        params = {
            'chebi_id': f"CHEBI:{self.metabolite_id}",
            'metabo_name': f"Metabolite {self.metabolite_id}",
            **params,
        }

        query = sql.text("INSERT INTO Metabolites VALUES (:chebi_id, :metabo_name)")
        self.db_conn.execute(query, params)

        return params
