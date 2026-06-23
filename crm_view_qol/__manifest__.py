# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    'name': "CRM - Views QoL",
    'version': '19.0.1.0.0',
    'icon': '/odootil/static/description/icon.png',
    'summary': 'Quality of Life improvements for CRM views',
    'license': 'AGPL-3',
    'author': 'Andrius Laukavičius',
    'website': 'https://timefordev.com',
    'category': 'Sales/CRM',
    'depends': [
        # odoo
        'crm',
    ],
    'data': [
        'views/crm_lead.xml',
    ],
    'installable': True,
}
