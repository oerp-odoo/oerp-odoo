# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale - Component Sticker Info",
    'version': '17.0.1.0.0',
    'summary': 'Base Product Component Sticker Info',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'sale',
    ],
    'data': [
        'views/product_category.xml',
        'views/product_template.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
}
