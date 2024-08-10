# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP Workorder - Multi Execute",
    'version': '15.0.1.0.0',
    'summary': 'Start/Block/Unblock/Pause/Finish multiple matching workorders at once',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp_workorder',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/mrp_workorder_multi_execute_views.xml',
    ],
    'installable': True,
}
