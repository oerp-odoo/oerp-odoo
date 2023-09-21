from odoo import _, fields, models
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

    def validate_stamp_type(self, stamp_type, raise_err=True):
        """Validate if given stamp_type matches category type."""
        self.ensure_one()
        if self.stamp_type != stamp_type:
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
