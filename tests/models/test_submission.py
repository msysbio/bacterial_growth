import tests.init  # noqa: F401

import unittest

import sqlalchemy as sql

from tests.database_test import DatabaseTest
from models.submission import Submission

class TestSubmission(DatabaseTest):
    def test_strains(self):
        t1 = self.create_taxon(tax_names="R. intestinalis")
        t2 = self.create_taxon(tax_names="B. thetaiotaomicron")

        submission = Submission({}, step=1, db_conn=self.db_conn)
        self.assertEqual(submission.fetch_strains(), [])

        submission = Submission({'strains': [t1['tax_id']]}, step=1, db_conn=self.db_conn)
        self.assertEqual(
            submission.fetch_strains(),
            [('1', 'R. intestinalis')],
        )

        submission.update_strains({'strains': [t1['tax_id'], t2['tax_id']], 'new_strains': []})
        self.assertEqual(
            submission.fetch_strains(),
            [('1', 'R. intestinalis'), ('2', 'B. thetaiotaomicron')],
        )

    def test_metabolites(self):
        m1 = self.create_metabolite(metabo_name="glucose")
        m2 = self.create_metabolite(metabo_name="trehalose")

        submission = Submission({}, step=1, db_conn=self.db_conn)
        self.assertEqual(submission.fetch_strains(), [])

        submission = Submission({'metabolites': [m1['chebi_id']]}, step=1, db_conn=self.db_conn)
        self.assertEqual(
            submission.fetch_metabolites(),
            [(m1['chebi_id'], 'glucose')],
        )

        submission = Submission(
            {'metabolites': [m1['chebi_id'], m2['chebi_id']]},
            step=1,
            db_conn=self.db_conn,
        )
        self.assertEqual(
            submission.fetch_metabolites(),
            [(m1['chebi_id'], 'glucose'), (m2['chebi_id'], 'trehalose')],
        )


if __name__ == '__main__':
    unittest.main()
