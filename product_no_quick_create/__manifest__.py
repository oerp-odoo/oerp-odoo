# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product - No quick create",
    'version': '15.0.1.0.0',
    'summary': 'Will not show quick create option on some product fields',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product',
    ],
    'data': ['views/product_supplierinfo_views.xml'],
    'installable': True,
}
