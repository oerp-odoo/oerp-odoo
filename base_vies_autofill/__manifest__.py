# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "VIES Customer Autofill",
    'version': '15.0.1.0.0',
    'summary': 'autofill, VIES, VAT, customer, API',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'base_vat',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
