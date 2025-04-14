import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from models import Metabolite
from tests.database_test import DatabaseTest


class TestMetabolite(DatabaseTest):
    def test_search_basic(self):
        self.create_metabolite(chebi_id="CHEBI:1", metabo_name="glucose")
        self.create_metabolite(chebi_id="CHEBI:2", metabo_name="trehalose")
        self.create_metabolite(chebi_id="CHEBI:3", metabo_name="lactate")

        results, _ = Metabolite.search_by_name(self.db_conn, 'glucose')
        self.assertEqual(
            ['glucose (CHEBI:1)'],
            [r['text'] for r in results]
        )

        # Matches are case-insensitive:
        results, _ = Metabolite.search_by_name(self.db_conn, 'Ose')
        self.assertEqual(
            sorted(['glucose (CHEBI:1)', 'trehalose (CHEBI:2)']),
            sorted([r['text'] for r in results])
        )

        results, _ = Metabolite.search_by_name(self.db_conn, '')
        self.assertEqual([], [r['text'] for r in results])

        results, _ = Metabolite.search_by_name(self.db_conn, ' ')
        self.assertEqual([], [r['text'] for r in results])

    def test_search_ordering_by_prefix_match(self):
        self.create_metabolite(chebi_id="CHEBI:1", metabo_name="glucose")
        self.create_metabolite(chebi_id="CHEBI:2", metabo_name="d-gluconic acid")

        # Matches at the beginning of the word are first:
        results, _ = Metabolite.search_by_name(self.db_conn, 'gluc')
        self.assertEqual(
            ['glucose (CHEBI:1)', 'd-gluconic acid (CHEBI:2)'],
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
