import init
import factories
from database_test import DatabaseTest

import unittest

from db_functions import *


class TestDbFunctions(DatabaseTest):
    def test_getInsertFieldValues(self):
        values = { 'foo': 'bar', 'Baz': 42 }
        result = getInsertFieldsValues(values)

        self.assertEqual(result, ['(foo,Baz)', "('bar','42')"])

        values = {}
        result = getInsertFieldsValues(values)

        self.assertEqual(result, ['', ''])

    def test_getChebiId(self):
        with self.db.cursor() as conn:
            metabolite1 = factories.create_metabolite(conn, metabo_name="Caffeine")
            metabolite2 = factories.create_metabolite(conn, metabo_name="Sucrose")

            self.db.commit()

            self.assertEqual(getChebiId("Caffeine"), metabolite1)
            self.assertEqual(getChebiId("Sucrose"), metabolite2)
            self.assertEqual(getChebiId("Nonexistent"), None)

    def test_getRecords_can_retrieve_studies(self):
        with self.db.cursor() as conn:
            study1 = factories.create_study(conn, studyName='Small study', projectUniqueID='p_small')
            study2 = factories.create_study(conn, studyName='Big study', projectUniqueID='p_big')

            self.db.commit()

            all_studies = getRecords('Study', {'studyName'}, {})
            all_studies.sort()
            self.assertEqual(all_studies, [('Big study',), ('Small study',)])

            big_studies = getRecords('Study', {'studyName'}, {'projectUniqueID': 'p_big'})
            self.assertEqual(big_studies, [('Big study',)])

if __name__ == '__main__':
    unittest.main()
