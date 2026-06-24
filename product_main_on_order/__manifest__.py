# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Main Product on Order",
    'version': '19.0.2.0.0',
    'summary': 'Rules to find main product on order',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_main_rule.xml',
    ],
    'installable': True,
}
