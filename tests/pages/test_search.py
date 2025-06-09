import tests.init  # noqa: F401

import unittest

from bs4 import BeautifulSoup

from tests.page_test import PageTest
from app.model.lib.dev import bootstrap_study


class TestSearch(PageTest):
    def test_basic(self):
        bootstrap_study(self.db_session, 'synthetic_gut', 'test_user')

        response = self.client.post('/search/', data={
            'clauses-0-value': 'Synthetic human gut',
        })

        self.assertEqual(response.status_code, 200)
        self.assertIn("Synthetic human gut bacterial community", self._get_text(response))


if __name__ == '__main__':
    unittest.main()
