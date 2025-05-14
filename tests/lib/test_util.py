import tests.init  # noqa: F401

import unittest
from types import SimpleNamespace

import lib.util as util


class TestUtil(unittest.TestCase):
    def test_group_by_unique_name(self):
        foo = SimpleNamespace(name="foo")
        bar = SimpleNamespace(name="bar")
        baz = SimpleNamespace(name="baz")

        self.assertEqual(
            util.group_by_unique_name([foo, bar]),
            {"foo": foo, "bar": bar},
        )
        self.assertEqual(
            util.group_by_unique_name([bar, baz]),
            {"bar": bar, "baz": baz},
        )

        with self.assertRaises(ValueError):
            util.group_by_unique_name([foo, bar, bar, baz])


if __name__ == '__main__':
    unittest.main()
