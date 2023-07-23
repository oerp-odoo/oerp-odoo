# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Source Document in Sale Orders Search Bar",
    'version': '15.0.1.0.0',
    'summary': 'Source document in Sale Order search view',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sale/Sale',
    'depends': [
        # odoo
        'sale',
    ],
    'data': [
        'views/sale_order_views.xml',
    ],
    'installable': False,
}
