# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Stock Moves Operation Report",
    'version': '15.0.1.0.0',
    'summary': 'Report to show product moves by source destination locations',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        'stock_account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/stock_move_operation_print_views.xml',
    ],
    'installable': True,
}
