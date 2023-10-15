from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

STAMP_TYPES = [
    ('die', "Die"),
    ('counter_die', "Counter Die"),
    ('mold', "Mold"),
]


# TODO: move this to more generic place.
def _get_selection_map(record, fname):
    return dict(record._fields[fname]._description_selection(record.env))


class ProductCategory(models.Model):
    _inherit = 'product.category'

    stamp_type = fields.Selection(
        STAMP_TYPES,
        copy=False,
    )
    nearest_stamp_type = fields.Selection(
        STAMP_TYPES,
        compute='_compute_nearest_stamp_type',
        store=True,
    )

    @api.depends(
        'stamp_type',
        'parent_id.nearest_stamp_type',
        'child_id.nearest_stamp_type',
        'parent_id.stamp_type',
        'child_id.stamp_type',
    )
    def _compute_nearest_stamp_type(self):
        for rec in self:
            rec.nearest_stamp_type = rec.get_nearest_stamp_type()

    def validate_stamp_type(self, stamp_type, raise_err=True):
        """Validate if given stamp_type matches nearest category type."""
        self.ensure_one()
        if self.nearest_stamp_type != stamp_type:
            if raise_err:
                selection_map = _get_selection_map(self, 'stamp_type')
                label = selection_map[stamp_type]
                raise ValidationError(
                    _(
                        "%(label)s must have Category (%(categ)s) with %(label)s type!",
                        label=label,
                        categ=self.name,
                    )
                )
            return False
        return True

    def get_nearest_stamp_type(self):
        self.ensure_one()
        if self.stamp_type:
            return self.stamp_type
        if self.parent_id:
            return self.parent_id.get_nearest_stamp_type()
        return False
