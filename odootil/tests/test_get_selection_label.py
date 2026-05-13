from odoo.tests.common import TransactionCase

SELECTION_FNAME = "font"


class TestGetSelectionLabel(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_main = cls.env.ref("base.main_company")

    def test_01_get_selection_label_selected(self):
        # GIVEN
        self.company_main[SELECTION_FNAME] = "Lato"
        # WHEN
        res = self.company_main.get_selection_label(SELECTION_FNAME)
        # THEN
        # This selection's values and labels are the same..
        self.assertEqual(res, "Lato")

    def test_02_get_selection_label_not_selected(self):
        # GIVEN
        self.company_main[SELECTION_FNAME] = False
        # WHEN
        res = self.company_main.get_selection_label(SELECTION_FNAME)
        # THEN
        self.assertEqual(res, "")
