# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale Orders Automatic Cleanup",
    'version': '19.0.2.0.0',
    'summary': 'Periodically clean up old unused sale orders.',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'sale',
    ],
    'external_dependencies': {'python': ['footil']},
    'data': [
        'security/ir.model.access.csv',
        'views/sale_autocacuum_rule.xml',
        'data/ir_cron.xml',
    ],
    'installable': True,
}
