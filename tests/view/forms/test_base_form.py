import tests.init  # noqa: F401

import unittest

from app.view.forms.base_form import _iterate_error_messages


class TestBaseForm(unittest.TestCase):
    def test_error_messages(self):
        # Simple error:
        errors = {"name": "is required"}
        messages = list(_iterate_error_messages(prefixes=[], errors=errors))
        self.assertEqual(messages, ["Name: is required"])

        # Name formatting
        errors = {"compartmentName": "is required"}
        messages = list(_iterate_error_messages(prefixes=[], errors=errors))
        self.assertEqual(messages, ["Compartment name: is required"])

        # List of errors:
        errors = {"object": ["foo is bar", "bar is baz"]}
        messages = list(_iterate_error_messages(prefixes=[], errors=errors))
        self.assertEqual(messages, ["Object: foo is bar", "Object: bar is baz"])

        # List of nested errors:
        errors = {
            "objects": [
                {"name": "invalid", "description": "invalid"},
                {"description": "invalid"},
            ]
        }
        messages = list(_iterate_error_messages(prefixes=[], errors=errors))
        self.assertEqual(
            messages,
            [
                "Objects 1 name: invalid",
                "Objects 1 description: invalid",
                "Objects 2 description: invalid",
            ],
        )

        # Complex tree of errors
        errors = {
            'experiments': [
                {
                    'name': ['is required'],
                    'bioreplicates': ["names are not unique"],
                },
                {
                    'name': ['is required'],
                },
                "names are not unique",
            ],
        }

        messages = list(_iterate_error_messages(prefixes=[], errors=errors))
        self.assertEqual(
            messages,
            [
                "Experiments 1 name: is required",
                "Experiments 1 bioreplicates: names are not unique",
                "Experiments 2 name: is required",
                "Experiments: names are not unique",
            ]
        )


if __name__ == '__main__':
    unittest.main()
