from odoo import api, fields, models

from ..value_objects.package_warning import PackageWarning


class PackageConfigurator(models.AbstractModel):
    _name = 'package.configurator'
    _description = "Package Configurator"

    state = fields.Selection(
        selection=[("draft", "Draft"), ("done", "Done")],
        default="draft",
        required=True,
    )
    base_length = fields.Float(required=True)
    base_width = fields.Float(required=True)
    base_height = fields.Float(required=True)
    company_id = fields.Many2one(
        'res.company', required=True, default=lambda s: s.env.company
    )
    description_warnings = fields.Html(compute='_compute_description_warnings')
    currency_id = fields.Many2one(related='company_id.currency_id')
    circulation_ids = fields.One2many(
        comodel_name='package.configurator.circulation',
        inverse_name='configurator_id',
        string="Circulations",
    )

    @api.depends('base_length', 'base_width', 'base_height')
    def _compute_description_warnings(self):
        for rec in self:
            warnings = rec.get_warnings()
            rec.description_warnings = self._format_description_warnings(warnings)

    def get_warnings(self) -> list[PackageWarning]:
        """Return warnings message if something is configured incorrectly.

        Extend to add warnings.
        """
        self.ensure_one()
        return []

    def _format_description_warnings(self, warnings: list[PackageWarning]):
        self.ensure_one()
        if not warnings:
            return False
        li_items = []
        for warning in warnings:
            klass = f'list-group-item list-group-item-{warning.warning_type.value}'
            li_items.append(f'<li class="{klass}">{warning.message}</li>')
        li_str = '\n'.join(li_items)
        return f'<ul class="list-group">{li_str}</ul>'
