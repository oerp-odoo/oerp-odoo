# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Accounting - Sold Quantities report",
    'version': '15.0.1.0.0',
    'summary': 'Generate CSV report for sold product quantities',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Accounting/Accounting',
    'depends': [
        # odoo
        'account',
    ],
    'data': [
        'security/ir.model.access.csv',
        'wizards/account_sold_qty_report_print_views.xml',
    ],
    'installable': True,
}
