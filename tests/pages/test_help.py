import tests.init  # noqa: F401

import unittest

from werkzeug.exceptions import NotFound

from tests.page_test import PageTest
from app.pages.help import HelpPages


class TestHelpPages(PageTest):
    def setUp(self):
        super().setUp()

        with self.app.app_context():
            self.help_pages = HelpPages()
            self.help_pages.process_once()

    def test_simple_page_rendering(self):
        self.assertIn(
            '<h2>Study navigation</h2>',
            str(self.help_pages.render_html('data-analysis')),
        )

        self.assertIn(
            'To upload a study,',
            str(self.help_pages.render_html('upload-process')),
        )

        with self.assertRaises(NotFound):
            self.help_pages.render_html('nonexistent')

    def test_searching(self):
        results = self.help_pages.search('upload a study,')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'upload-process')
        self.assertIn(
            """To <span class="highlight">upload a study,</span> first""",
            results[0]['excerpt_html']
        )


if __name__ == '__main__':
    unittest.main()
