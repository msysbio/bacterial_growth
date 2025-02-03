import init
import factories
from database_test import DatabaseTest

import unittest

import db_functions


class TestDbFunctions(DatabaseTest):
    def test_getInsertFieldValues(self):
        values = {'foo': 'bar', 'Baz': 42}
        result = db_functions.getInsertFieldsValues(values)

        self.assertEqual(result, ['(foo,Baz)', "('bar','42')"])

        values = {}
        result = db_functions.getInsertFieldsValues(values)

        self.assertEqual(result, ['', ''])

    def test_getChebiId(self):
        with self.db.cursor() as conn:
            metabolite1 = factories.create_metabolite(conn, metabo_name="Caffeine")
            metabolite2 = factories.create_metabolite(conn, metabo_name="Sucrose")

            self.db.commit()

            self.assertEqual(db_functions.getChebiId("Caffeine"), metabolite1)
            self.assertEqual(db_functions.getChebiId("Sucrose"), metabolite2)
            self.assertEqual(db_functions.getChebiId("Nonexistent"), None)

    def test_getRecords_can_retrieve_studies(self):
        with self.db.cursor() as conn:
            factories.create_study(conn, studyName='Small study', projectUniqueID='p_small')
            factories.create_study(conn, studyName='Big study', projectUniqueID='p_big')

            self.db.commit()

            all_studies = db_functions.getRecords('Study', {'studyName'}, {})
            all_studies.sort()
            self.assertEqual(all_studies, [('Big study',), ('Small study',)])

            big_studies = db_functions.getRecords('Study', {'studyName'}, {'projectUniqueID': 'p_big'})
            self.assertEqual(big_studies, [('Big study',)])

    def test_getStudyID(self):
        # Create 2 studies
        with self.db.cursor() as conn:
            factories.create_study(conn)
            factories.create_study(conn)
            self.db.commit()

        st_conn = self.create_streamlit_connection()

        # Next study will have an ID of 3
        self.assertEqual(db_functions.getStudyID(st_conn), "SMGDB00000003")

        # Create 1 study
        with self.db.cursor() as conn:
            factories.create_study(conn)
            self.db.commit()

        # Next study will have an ID of 4
        self.assertEqual(db_functions.getStudyID(st_conn), "SMGDB00000004")


if __name__ == '__main__':
    unittest.main()
