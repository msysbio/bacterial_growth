import tests.init  # noqa: F401

import unittest

from tests.page_test import PageTest
from app.model.lib.dev import bootstrap_study


class TestSearch(PageTest):
    def setUp(self):
        super().setUp()

        self._bootstrap_taxa()
        self._bootstrap_metabolites()

    def test_no_query(self):
        bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')
        bootstrap_study(self.db_session, 'ri_bt_bh_in_chemostat_controls', 'test_user')

        response = self.client.get('/search/')
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic human gut bacterial community", response_text)
        self.assertIn("RI, BT and BH in chemostat: Controls", response_text)

        response = self.client.get('/search/', query_string={'clauses-0-value': ''})
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic human gut bacterial community", response_text)
        self.assertIn("RI, BT and BH in chemostat: Controls", response_text)

    def test_basic_query(self):
        s1 = bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')
        s2 = bootstrap_study(self.db_session, 'ri_bt_bh_in_chemostat_controls', 'test_user')

        response = self.client.get('/search/', query_string={
            'clauses-0-option': 'Study Name',
            'clauses-0-value': 'Synthetic human gut',
        })
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic human gut bacterial community", response_text)
        self.assertNotIn("RI, BT and BH in chemostat: Controls", response_text)

        response = self.client.get('/search/', query_string={
            'clauses-0-option': 'Study Name',
            'clauses-0-value': 'chemostat',
        })
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Synthetic human gut bacterial community", response_text)
        self.assertIn("RI, BT and BH in chemostat: Controls", response_text)

        # Only published ones should be shown:
        s1.publishedAt = None
        self.db_session.add(s1)
        self.db_session.commit()

        response = self.client.get('/search/')
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Synthetic human gut bacterial community", response_text)
        self.assertIn("RI, BT and BH in chemostat: Controls", response_text)



if __name__ == '__main__':
    unittest.main()
