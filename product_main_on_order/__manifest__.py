# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Main Product on Order",
    'version': '15.0.1.0.1',
    'summary': 'Rules to find main product on order',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_main_rule_views.xml',
    ],
    'demo': [
        'demo/product_main_rule.xml',
    ],
    'installable': False,
}
