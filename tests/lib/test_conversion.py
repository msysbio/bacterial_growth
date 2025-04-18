import unittest

from lib.conversion import convert_time


class TestConversion(unittest.TestCase):
    def test_time_conversion_to_the_same_unit(self):
        for t in (1, 0.3, 100.0, 0.5):
            for unit in ('d', 'h', 'm', 's'):
                self.assertEqual(convert_time(t, source=unit, target=unit), t)

    def test_time_conversion_to_seconds(self):
        for t in (1, 13, 100.0, 0.5):
            self.assertEqual(convert_time(t, source='m', target='s'), t * 60)
            self.assertEqual(convert_time(t, source='h', target='s'), t * 60 * 60)
            self.assertEqual(convert_time(t, source='d', target='s'), t * 24 * 60 * 60)

    def test_time_conversion_down(self):
        self.assertEqual(convert_time(1, source='d', target='h'), 24)
        self.assertEqual(convert_time(1, source='h', target='m'), 60)
        self.assertEqual(convert_time(0.5, source='h', target='m'), 30)

    def test_time_conversion_up(self):
        for t in (1, 13, 100.0, 0.5):
            self.assertEqual(convert_time(t * 60,           target='m', source='s'), t)
            self.assertEqual(convert_time(t * 60 * 60,      target='h', source='s'), t)
            self.assertEqual(convert_time(t * 24 * 60 * 60, target='d', source='s'), t)

    def test_time_conversion_rounding(self):
        self.assertEqual(convert_time(3600, source='s', target='h'), 1)
        self.assertEqual(convert_time(5400, source='s', target='h'), 1.5)

        # Rounded to 2 decimals after the dot
        self.assertEqual(convert_time(3500, source='s', target='h'), 0.97)

    def test_time_conversion_unknown_units(self):
        with self.assertRaises(ValueError): convert_time(1, source='s', target='unknown')
        with self.assertRaises(ValueError): convert_time(1, target='s', source='unknown')


if __name__ == '__main__':
    unittest.main()
