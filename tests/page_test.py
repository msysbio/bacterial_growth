import tests.init  # noqa: F401

import unittest

from bs4 import BeautifulSoup

from main import create_app
from tests.database_test import DatabaseTest

TAXON_NAMES = {
    "818":    "Bacteroides thetaiotaomicron",
    "53443":  "Blautia hydrogenotrophica",
    "74426":  "Collinsella aerofaciens",
    "166486": "Roseburia intestinalis",
    "476272": "Blautia hydrogenotrophica DSM 10507",
    "537011": "Prevotella copri DSM 18205",
}

METABOLITE_NAMES = {
    "CHEBI:422":   "(s)-lactic acid",
    "CHEBI:15361": "pyruvate",
    "CHEBI:15366": "acetic acid",
    "CHEBI:15740": "formate",
    "CHEBI:15741": "succinic acid",
    "CHEBI:16236": "ethanol",
    "CHEBI:17012": "n-acetylneuraminic acid",
    "CHEBI:17234": "glucose",
    "CHEBI:17272": "propionate",
    "CHEBI:17418": "valeric acid",
    "CHEBI:17968": "butyrate",
    "CHEBI:24996": "lactate",
    "CHEBI:26806": "succinate",
    "CHEBI:27082": "trehalose",
    "CHEBI:28260": "galactose",
    "CHEBI:30089": "acetate",
    "CHEBI:30751": "formic acid",
    "CHEBI:30772": "butyric acid",
    "CHEBI:32816": "pyruvic acid",
    "CHEBI:33984": "fucose",
    "CHEBI:37684": "mannose",
}


class PageTest(DatabaseTest):
    def setUp(self):
        super().setUp()

        self.app    = create_app()
        self.client = self.app.test_client()

    def _bootstrap_taxa(self):
        for ncbi_id, name in TAXON_NAMES.items():
            self.create_taxon(ncbiId=ncbi_id, name=name)

    def _bootstrap_metabolites(self):
        for chebi_id, name in METABOLITE_NAMES.items():
            self.create_metabolite(chebiId=chebi_id, name=name)

    def _get_text(self, response):
        soup = BeautifulSoup(response.data, 'html.parser')
        return soup.get_text(' | ', strip=True)
