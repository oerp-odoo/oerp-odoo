# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    'name': 'Stock - Auto Finish Chain',
    'version': '17.0.1.0.0',
    'summary': 'Auto finish Chained pickings by rules',
    'license': 'LGPL-3',
    'author': 'Andrius Laukavičius',
    'website': 'https://timefordev.com',
    'category': 'Inventory/Inventory',
    'depends': [
        # odoo
        'stock',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/stock_chain_rule_security.xml',
        'views/stock_chain_rule.xml',
    ],
    'installable': True,
}
