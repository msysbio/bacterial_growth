import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from models.taxon import Taxon
from tests.database_test import DatabaseTest


class TestTaxon(DatabaseTest):
    def test_search_basic(self):
        self.create_taxon(tax_names="Vibrio pelagius")
        self.create_taxon(tax_names="Anaerovibrio")
        self.create_taxon(tax_names="Brevibacterium linens")

        results, _ = Taxon.search_by_name(self.db_conn, 'pelagius')
        self.assertEqual(
            ['Vibrio pelagius'],
            [r['text'] for r in results]
        )

        results, _ = Taxon.search_by_name(self.db_conn, 'vib')
        self.assertEqual(
            sorted(['Vibrio pelagius', 'Anaerovibrio', 'Brevibacterium linens']),
            sorted([r['text'] for r in results])
        )

    def test_search_ordering_by_prefix_match(self):
        self.create_taxon(tax_names="Vibrio pelagius")
        self.create_taxon(tax_names="Vibrio anguillarum")
        self.create_taxon(tax_names="Anaerovibrio")
        self.create_taxon(tax_names="Panaeolus")

        results, _ = Taxon.search_by_name(self.db_conn, 'vib')
        self.assertEqual(
            ['Vibrio anguillarum', 'Vibrio pelagius', 'Anaerovibrio'],
            [r['text'] for r in results]
        )

        results, _ = Taxon.search_by_name(self.db_conn, 'anae')
        self.assertEqual(
            ['Anaerovibrio', 'Panaeolus'],
            [r['text'] for r in results]
        )

if __name__ == '__main__':
    unittest.main()
