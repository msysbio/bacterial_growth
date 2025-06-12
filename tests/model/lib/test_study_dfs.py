import tests.init  # noqa: F401

import unittest
import re

import app.model.lib.study_dfs as study_dfs


class TestStudyDsf(unittest.TestCase):
    def assertSqlQuery(self, actual, expected):
        actual   = ' '.join(re.split(r'\s+', actual.strip(), flags=re.MULTILINE))
        expected = ' '.join(re.split(r'\s+', expected.strip(), flags=re.MULTILINE))

        actual   = re.sub(r'\s*;$', '', actual, flags=re.MULTILINE)
        expected = re.sub(r'\s*;$', '', expected, flags=re.MULTILINE)

        self.assertEqual(actual, expected)

    def test_dynamical_query_with_simple_arguments(self):
        query, values = study_dfs.dynamical_query([
            {'option': 'Study Name', 'value': 'Example'}
        ])
        self.assertSqlQuery(query, """
            SELECT DISTINCT studyId
            FROM Studies
            WHERE LOWER(studyName) LIKE :value_0
        """)
        self.assertEqual(values, ['%example%'])

        query, values = study_dfs.dynamical_query([
            {'option': 'Microbial Strain', 'value': 'Rhodospirillum'}
        ])
        self.assertSqlQuery(query, """
            SELECT DISTINCT studyId
            FROM Strains
            WHERE LOWER(name) LIKE :value_0
        """)
        self.assertEqual(values, ['%rhodospirillum%'])

    def test_dynamical_query_with_logic_operators(self):
        query, values = study_dfs.dynamical_query([
            {'option': 'Study Name', 'value': 'human'},
            {'option': 'Metabolites', 'value': 'acetyl', 'logic_operator': 'AND'}
        ])
        self.assertSqlQuery(query, """
            SELECT DISTINCT studyId
            FROM Studies
            WHERE LOWER(studyName) LIKE :value_0
            AND studyId IN (
                SELECT DISTINCT studyId
                FROM StudyMetabolites
                INNER JOIN Metabolites ON Metabolites.chebiId = StudyMetabolites.chebi_id
                WHERE LOWER(Metabolites.name) LIKE :value_1
            )
        """)
        self.assertEqual(values, ['%human%', '%acetyl%'])


if __name__ == '__main__':
    unittest.main()
