# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Product Category Group - MRP/Purchase",
    'version': '17.0.1.0.0',
    'summary': 'Integrate sale product category group names with MRP and purchase',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'sale_mrp',
        'sale_purchase',
        'purchase_stock',
        # oerp-odoo
        'sale_product_categ_group',
    ],
    'data': [
        'views/mrp_production.xml',
        'views/purchase_order.xml',
    ],
    'installable': True,
}
