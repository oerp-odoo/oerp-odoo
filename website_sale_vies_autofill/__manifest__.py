# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "VIES Customer Autofill - Checkout Address",
    'version': '15.0.1.0.0',
    'summary': 'autofill, VIES, VAT, customer, API, ecommerce, eshop, address',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Website/Website',
    'depends': [
        # odoo
        'website_sale',
        # oerp-odoo
        'base_vies_autofill',
    ],
    'data': [
        # 'views/res_config_settings_views.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'website_sale_vies_autofill/static/src/js/website_sale.esm.js',
        ]
    },
    'installable': False,
}
