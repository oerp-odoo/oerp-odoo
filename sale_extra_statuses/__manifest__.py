# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
# TODO: it should be two separate modules, one for purchase status,
# another for mrp.
{
    "name": "Sale Extra Statuses",
    "version": "17.0.1.0.0",
    "summary": "Show extra statuses on sale orders",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Sales/Sales",
    "depends": [
        # oerp-odoo
        "sale_stock_primary_link_purchase",
        "sale_stock_primary_link_mrp",
    ],
    "data": ["views/sale_order.xml"],
    "installable": True,
}
