import flask_app.tests.init

import unittest
import re

import flask_app.models.study_dfs as study_dfs

class TestStudyDsf(unittest.TestCase):
    def assertSqlQuery(self, actual, expected):
        actual   = ' '.join(re.split(r'\s+', actual.strip(), flags=re.MULTILINE))
        expected = ' '.join(re.split(r'\s+', expected.strip(), flags=re.MULTILINE))

        actual   = re.sub(r'\s*;$', '', actual, flags=re.MULTILINE)
        expected = re.sub(r'\s*;$', '', expected, flags=re.MULTILINE)

        self.assertEqual(actual, expected)

    def test_dynamical_query_with_simple_arguments(self):
        query = study_dfs.dynamical_query([
            {'option': 'Study Name', 'value': 'Example'}
        ])
        self.assertSqlQuery(query, """
            SELECT DISTINCT studyId
            FROM Study
            WHERE studyName LIKE '%Example%'
        """)

        query = study_dfs.dynamical_query([
            {'option': 'Microbial Strain', 'value': 'Rhodospirillum'}
        ])
        self.assertSqlQuery(query, """
            SELECT DISTINCT studyId
            FROM Strains
            WHERE memberName LIKE '%Rhodospirillum%'
        """)

    def test_dynamical_query_with_logic_operators(self):
        query = study_dfs.dynamical_query([
            {'option': 'Study Name', 'value': 'human'},
            {'option': 'Metabolites', 'value': 'acetyl', 'logic_operator': 'AND'}
        ])
        self.assertSqlQuery(query, """
            SELECT DISTINCT studyId
            FROM Study
            WHERE studyName LIKE '%human%'
            AND studyId IN (
                SELECT DISTINCT studyId
                FROM MetabolitePerExperiment
                WHERE metabo_name LIKE '%acetyl%'
            )
        """)

if __name__ == '__main__':
    unittest.main()
