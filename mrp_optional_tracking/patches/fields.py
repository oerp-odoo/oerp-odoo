from odoo.fields import Selection

from ..utils import get_product_mrp_tracking

orig_get = Selection.__get__


def __get__(self, record, owner):
    ctx = record.env.context
    if (
        record._name == 'product.product'
        and self.name == 'tracking'
        # Use mrp tracking if we are on mrp.production model only!
        and ctx.get('params', {}).get('model') == 'mrp.production'
        and not ctx.get('product_mrp_tracking_consumed')
    ):
        return get_product_mrp_tracking(
            record.with_context(product_mrp_tracking_consumed=True)
        )
    return orig_get(self, record, owner)


Selection.__get__ = __get__
