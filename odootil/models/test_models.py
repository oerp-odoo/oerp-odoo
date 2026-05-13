from odoo import api, fields, models

from ..tools.validation import check_field_unique

FIELDS_MAP_1 = {
    'number': "Number",
    'mobile': "Mobile",
}


class OdootilIsDefaultTestSingle(models.Model):
    _name = 'odootil.is_default.test.single'
    _description = "Odootil Is Default Test Single"
    _inherit = 'odootil.is_default.mixin'
    _is_default_single = True

    name = fields.Char(required=True)


class OdootilIsDefaultTestSingleMultiCompany(models.Model):
    _name = 'odootil.is_default.test.single.multicompany'
    _description = "Odootil Is Default Test Single Multi-Company"
    _inherit = 'odootil.is_default.mixin'
    _is_default_single = True

    name = fields.Char(required=True)
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company)
    active = fields.Boolean(default=True)


class OdootilIsDefaultTestMulti(models.Model):
    _name = 'odootil.is_default.test.multi'
    _description = "Odootil Is Default Test Multi"
    _inherit = 'odootil.is_default.mixin'
    _is_default_single = False

    name = fields.Char(required=True)


class OdootilTestFieldUnique(models.Model):
    _name = 'odootil.test.field.unique'
    _description = "Odootil Test Field Unique"

    name = fields.Char(required=True)
    code = fields.Char(copy=False)
    is_default = fields.Boolean()


class OdootilTestFieldUniqueMultiCompany(models.Model):
    _name = 'odootil.test.field.unique.multicompany'
    _description = "Odootil Test Field Unique Multi-Company"
    _inherit = 'odootil.test.field.unique'

    name = fields.Char(required=True)
    code = fields.Char(copy=False)
    company_id = fields.Many2one('res.company', default=lambda s: s.env.company)
    active = fields.Boolean(default=True)

    @api.constrains('code', 'company_id', 'active')
    def _check_code_unique(self):
        check_field_unique(self, 'code')


class OdootilTestStripSpace(models.Model):
    _name = 'odootil.strip_space.test'
    _description = "Odootil Test Strip Whitespaces"
    _inherit = 'odootil.strip_space'

    name = fields.Char(required=True)
    code = fields.Char()

    @property
    def strip_space_fields(self):
        return super().strip_space_fields + ['name', 'code']
