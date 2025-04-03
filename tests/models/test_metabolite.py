import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from models import Metabolite
from tests.database_test import DatabaseTest


class TestMetabolite(DatabaseTest):
    def test_search_basic(self):
        self.create_metabolite(metabo_name="Vibrio pelagius")
        self.create_metabolite(metabo_name="Anaerovibrio")
        self.create_metabolite(metabo_name="Brevibacterium linens")

        results, _ = Metabolite.search_by_name(self.db_conn, 'pelagius')
        self.assertEqual(
            ['Vibrio pelagius'],
            [r['text'] for r in results]
        )

        # Matches are case-insensitive:
        results, _ = Metabolite.search_by_name(self.db_conn, 'vib')
        self.assertEqual(
            sorted(['Vibrio pelagius', 'Anaerovibrio', 'Brevibacterium linens']),
            sorted([r['text'] for r in results])
        )

        results, _ = Metabolite.search_by_name(self.db_conn, '')
        self.assertEqual([], [r['text'] for r in results])

        results, _ = Metabolite.search_by_name(self.db_conn, ' ')
        self.assertEqual([], [r['text'] for r in results])

    def test_search_ordering_by_prefix_match(self):
        self.create_metabolite(metabo_name="Vibrio pelagius")
        self.create_metabolite(metabo_name="Vibrio anguillarum")
        self.create_metabolite(metabo_name="Anaerovibrio")
        self.create_metabolite(metabo_name="Panaeolus")

        # Matches at the beginning of the word are first:
        results, _ = Metabolite.search_by_name(self.db_conn, 'vib')
        self.assertEqual(
            ['Vibrio anguillarum', 'Vibrio pelagius', 'Anaerovibrio'],
            [r['text'] for r in results]
        )

        results, _ = Metabolite.search_by_name(self.db_conn, 'anae')
        self.assertEqual(
            ['Anaerovibrio', 'Panaeolus'],
            [r['text'] for r in results]
        )

    def test_search_by_multiple_words(self):
        self.create_metabolite(metabo_name="Salmonella enterica serovar Infantis")
        self.create_metabolite(metabo_name="Salmonella enterica serovar Moscow")

        # Words are searched separately:
        results, _ = Metabolite.search_by_name(self.db_conn, 'salmonella infantis')
        self.assertEqual(
            ['Salmonella enterica serovar Infantis'],
            [r['text'] for r in results]
        )

        # Words are searched in order:
        results, _ = Metabolite.search_by_name(self.db_conn, 'infantis salmonella')
        self.assertEqual(
            [],
            [r['text'] for r in results]
        )

    def test_pagination(self):
        self.create_metabolite(metabo_name="Test 1 foo")
        self.create_metabolite(metabo_name="Test 2 foo")
        self.create_metabolite(metabo_name="Test 3 bar")
        self.create_metabolite(metabo_name="Test 4 bar")

        # Two per page, two pages:
        results, has_more = Metabolite.search_by_name(self.db_conn, 'Test', page=1, per_page=2)
        self.assertEqual(len(results), 2)
        self.assertTrue(has_more)

        results, has_more = Metabolite.search_by_name(self.db_conn, 'Test', page=2, per_page=2)
        self.assertEqual(len(results), 2)
        self.assertFalse(has_more)

        # Three per page, two pages:
        results, has_more = Metabolite.search_by_name(self.db_conn, 'Test', page=1, per_page=3)
        self.assertEqual(len(results), 3)
        self.assertTrue(has_more)

        results, has_more = Metabolite.search_by_name(self.db_conn, 'Test', page=2, per_page=3)
        self.assertEqual(len(results), 1)
        self.assertFalse(has_more)

        # Page ten, no results:
        results, has_more = Metabolite.search_by_name(self.db_conn, 'Test', page=10, per_page=3)
        self.assertEqual(len(results), 0)
        self.assertFalse(has_more)

        # Pagination correctly takes into account two-word searches:
        results, has_more = Metabolite.search_by_name(self.db_conn, 'Test foo', page=1, per_page=1)
        self.assertEqual(len(results), 1)
        self.assertTrue(has_more)

if __name__ == '__main__':
    unittest.main()
