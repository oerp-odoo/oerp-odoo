# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "CRM - Team Required",
    'version': '19.0.1.0.0',
    'summary': 'Makes team required on lead/opportunity',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # odoo
        'crm',
    ],
    'data': [
        'views/crm_lead.xml',
    ],
    'installable': True,
}
