import tests.init  # noqa: F401

import unittest

from bs4 import BeautifulSoup

from tests.page_test import PageTest
from app.model.lib.dev import bootstrap_study


class TestSearch(PageTest):
    def test_no_query(self):
        bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')
        bootstrap_study(self.db_session, 'ri_bt_bh_in_chemostat_controls', 'test_user')

        response = self.client.post('/search/', data={
            'clauses-0-value': 'Synthetic human gut',
        })
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic human gut bacterial community", response_text)
        self.assertIn("RI, BT and BH in chemostat: Controls", response_text)


    def test_basic_query(self):
        bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')
        bootstrap_study(self.db_session, 'ri_bt_bh_in_chemostat_controls', 'test_user')

        response = self.client.post('/search/', data={
            'clauses-0-option': 'Study Name',
            'clauses-0-value': 'Synthetic human gut',
        })
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic human gut bacterial community", response_text)
        self.assertNotIn("RI, BT and BH in chemostat: Controls", response_text)

        response = self.client.post('/search/', data={
            'clauses-0-option': 'Study Name',
            'clauses-0-value': 'chemostat',
        })
        response_text = self._get_text(response)

        self.assertEqual(response.status_code, 200)
        self.assertNotIn("Synthetic human gut bacterial community", response_text)
        self.assertIn("RI, BT and BH in chemostat: Controls", response_text)


if __name__ == '__main__':
    unittest.main()
