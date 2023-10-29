# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Sale - Custom Confirm Email per Payment Acquirer",
    'version': '15.0.1.0.0',
    'summary': 'Can choose custom confirm email template on payment acquirer',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sale/Sale',
    'depends': [
        # odoo
        'sale',
    ],
    'data': ['views/payment_acquirer_views.xml'],
    'installable': True,
}
