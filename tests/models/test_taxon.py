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

        # Matches are case-insensitive:
        results, _ = Taxon.search_by_name(self.db_conn, 'vib')
        self.assertEqual(
            sorted(['Vibrio pelagius', 'Anaerovibrio', 'Brevibacterium linens']),
            sorted([r['text'] for r in results])
        )

        results, _ = Taxon.search_by_name(self.db_conn, '')
        self.assertEqual([], [r['text'] for r in results])

        results, _ = Taxon.search_by_name(self.db_conn, ' ')
        self.assertEqual([], [r['text'] for r in results])

    def test_search_ordering_by_prefix_match(self):
        self.create_taxon(tax_names="Vibrio pelagius")
        self.create_taxon(tax_names="Vibrio anguillarum")
        self.create_taxon(tax_names="Anaerovibrio")
        self.create_taxon(tax_names="Panaeolus")

        # Matches at the beginning of the word are first:
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

    def test_search_by_multiple_words(self):
        self.create_taxon(tax_names="Salmonella enterica serovar Infantis")
        self.create_taxon(tax_names="Salmonella enterica serovar Moscow")

        # Words are searched separately:
        results, _ = Taxon.search_by_name(self.db_conn, 'salmonella infantis')
        self.assertEqual(
            ['Salmonella enterica serovar Infantis'],
            [r['text'] for r in results]
        )

        # Words are searched in order:
        results, _ = Taxon.search_by_name(self.db_conn, 'infantis salmonella')
        self.assertEqual(
            [],
            [r['text'] for r in results]
        )

    def test_pagination(self):
        self.create_taxon(tax_names="Test 1 foo")
        self.create_taxon(tax_names="Test 2 foo")
        self.create_taxon(tax_names="Test 3 bar")
        self.create_taxon(tax_names="Test 4 bar")

        # Two per page, two pages:
        results, has_more = Taxon.search_by_name(self.db_conn, 'Test', page=1, per_page=2)
        self.assertEqual(len(results), 2)
        self.assertTrue(has_more)

        results, has_more = Taxon.search_by_name(self.db_conn, 'Test', page=2, per_page=2)
        self.assertEqual(len(results), 2)
        self.assertFalse(has_more)

        # Three per page, two pages:
        results, has_more = Taxon.search_by_name(self.db_conn, 'Test', page=1, per_page=3)
        self.assertEqual(len(results), 3)
        self.assertTrue(has_more)

        results, has_more = Taxon.search_by_name(self.db_conn, 'Test', page=2, per_page=3)
        self.assertEqual(len(results), 1)
        self.assertFalse(has_more)

        # Page ten, no results:
        results, has_more = Taxon.search_by_name(self.db_conn, 'Test', page=10, per_page=3)
        self.assertEqual(len(results), 0)
        self.assertFalse(has_more)

        # Pagination correctly takes into account two-word searches:
        results, has_more = Taxon.search_by_name(self.db_conn, 'Test foo', page=1, per_page=1)
        self.assertEqual(len(results), 1)
        self.assertTrue(has_more)

if __name__ == '__main__':
    unittest.main()
