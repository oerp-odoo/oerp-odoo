# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Pricelist Code",
    'version': '15.0.1.0.0',
    'summary': 'Identifier for pricelists',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'views/product_pricelist_views.xml',
    ],
    'installable': True,
}
