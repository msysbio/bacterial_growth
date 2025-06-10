import tests.init  # noqa: F401

import unittest
from tempfile import TemporaryDirectory
from pathlib import Path

from flask import render_template

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
            '<h2>How to upload my data?</h2>',
            str(self.help_pages.render_html('uploading-process')),
        )

        with self.assertRaises(KeyError):
            self.help_pages.render_html('nonexistent')

    def test_searching(self):
        results = self.help_pages.search('upload your data')

        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['name'], 'uploading-process')
        self.assertIn(
            """To <span class="highlight">upload your data</span> in µGrowthDB""",
            results[0]['excerpt_html']
        )



if __name__ == '__main__':
    unittest.main()
