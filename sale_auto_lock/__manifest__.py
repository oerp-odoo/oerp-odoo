# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Order Auto Lock",
    'version': '15.0.1.0.0',
    'summary': 'Auto lock sale order if all related documents are fulfilled',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sale',
    'depends': [
        # odoo
        'sale_stock',
    ],
    'data': [
        'data/ir_cron_data.xml',
    ],
    'installable': False,
}
