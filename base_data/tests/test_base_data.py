from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestBaseData(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.BaseData = cls.env['base.data']
        cls.BaseDataLabel = cls.env['base.data.label']
        cls.model_res_partner = cls.env.ref('base.model_res_partner')
        cls.label_1, cls.label_2 = cls.BaseDataLabel.create(
            [{'name': 'MY-L1'}, {'name': 'MY-L2'}]
        )
        cls.base_datas = cls.BaseData.create(
            [
                {
                    'name': 'MY-D1',
                    'model_id': cls.model_res_partner.id,
                    'defaults': "{'name': 'MY-P1'}",
                },
                {
                    'name': 'MY-D1',
                    'model_id': cls.model_res_partner.id,
                    'defaults': "{'name': 'MY-P2'}",
                    "label_ids": [(4, cls.label_1.id)],
                },
                {
                    'name': 'MY-D1',
                    'model_id': cls.model_res_partner.id,
                    'defaults': "{'name': 'MY-P3'}",
                    "label_ids": [(4, cls.label_2.id)],
                },
                {
                    'name': 'MY-D1',
                    'model_id': cls.model_res_partner.id,
                    'defaults': "{'name': 'MY-P4'}",
                    "label_ids": [(4, cls.label_1.id), (4, cls.label_2.id)],
                },
            ]
        )

    def test_01_get_data_matched_no_labels(self):
        # WHEN
        data = self.BaseData.get_data('MY-D1', 'res.partner')
        # THEN
        self.assertEqual(data, {'name': 'MY-P1'})

    def test_02_get_data_no_labels_inactive(self):
        # GIVEN
        self.base_datas[0].active = False
        # WHEN
        data = self.BaseData.get_data('MY-D1', 'res.partner')
        # THEN
        self.assertEqual(data, {})

    def test_03_get_data_matched_one_label(self):
        # WHEN
        data = self.BaseData.get_data(
            'MY-D1', 'res.partner', labels=frozenset(['MY-L1'])
        )
        # THEN
        self.assertEqual(data, {'name': 'MY-P2'})

    def test_04_get_data_matched_two_labels(self):
        # WHEN
        data = self.BaseData.get_data(
            'MY-D1', 'res.partner', labels=frozenset(['MY-L1', 'MY-L2'])
        )
        # THEN
        self.assertEqual(data, {'name': 'MY-P4'})

    def test_05_base_data_have_same_keys_no_labels(self):
        with self.assertRaisesRegex(
            ValidationError, r"Data keys must be unique \(name, model, labels\)!"
        ):
            self.BaseData.create(
                {'name': 'MY-D1', 'model_id': self.model_res_partner.id}
            )

    def test_06_base_data_have_same_keys_one_label(self):
        with self.assertRaisesRegex(
            ValidationError, r"Data keys must be unique \(name, model, labels\)!"
        ):
            self.BaseData.create(
                {
                    'name': 'MY-D1',
                    'model_id': self.model_res_partner.id,
                    'label_ids': [(4, self.label_1.id)],
                }
            )

    def test_07_base_data_have_same_keys_two_labels(self):
        with self.assertRaisesRegex(
            ValidationError, r"Data keys must be unique \(name, model, labels\)!"
        ):
            self.BaseData.create(
                {
                    'name': 'MY-D1',
                    'model_id': self.model_res_partner.id,
                    'label_ids': [(4, self.label_2.id), (4, self.label_1.id)],
                }
            )

    def test_08_base_data_defaults_cant_eval(self):
        with self.assertRaisesRegex(
            ValidationError, r"Defaults must be dictionary\. Error: .+"
        ):
            self.base_datas[0].defaults = "abc"

    def test_09_base_data_defaults_not_dict(self):
        with self.assertRaisesRegex(ValidationError, r"Defaults must be dictionary\."):
            self.base_datas[0].defaults = "'abc'"
