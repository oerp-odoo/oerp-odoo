from lxml import etree

from odoo.tests.common import TransactionCase

from ..tools.view import preprocess_arch_readonly_fields


class TestView(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']

    def test_01_preprocess_arch_readonly_fields(self):
        # GIVEN
        arch = self.ResPartner.get_view(view_type='form')['arch']
        # WHEN
        res = preprocess_arch_readonly_fields(self.ResPartner, arch, 'my_custom_state')
        # THEN
        new_archnode = etree.fromstring(res)
        field_node_email = new_archnode.xpath("//field[@name='email']")[0]
        self.assertEqual('my_custom_state', field_node_email.get('readonly'))

    def test_02_preprocess_arch_readonly_fields_excluded(self):
        # GIVEN
        arch = self.ResPartner.get_view(view_type='form')['arch']
        # WHEN
        res = preprocess_arch_readonly_fields(
            self.ResPartner, arch, 'my_custom_state', ignored_fields=['is_company']
        )
        # THEN
        new_archnode = etree.fromstring(res)
        field_node_email = new_archnode.xpath("//field[@name='email']")[0]
        field_node_is_company = new_archnode.xpath("//field[@name='is_company']")[0]
        self.assertEqual('my_custom_state', field_node_email.get('readonly'))
        self.assertFalse(field_node_is_company.get('readonly'))

    def test_03_preprocess_arch_readonly_fields_subview(self):
        """Fields of an embedded subview are left to their own model."""
        # GIVEN
        arch = """
            <form>
                <field name="email"/>
                <field name="bank_ids">
                    <list>
                        <field name="acc_number"/>
                    </list>
                </field>
            </form>
        """
        # WHEN
        res = preprocess_arch_readonly_fields(self.ResPartner, arch, 'my_custom_state')
        # THEN
        new_archnode = etree.fromstring(res)
        field_node_email = new_archnode.xpath("//field[@name='email']")[0]
        field_node_bank_ids = new_archnode.xpath("//field[@name='bank_ids']")[0]
        field_node_acc_number = new_archnode.xpath("//field[@name='acc_number']")[0]
        self.assertEqual('my_custom_state', field_node_email.get('readonly'))
        self.assertEqual('my_custom_state', field_node_bank_ids.get('readonly'))
        self.assertFalse(field_node_acc_number.get('readonly'))
