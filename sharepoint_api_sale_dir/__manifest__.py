# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MS Sharepoint API - Sale Documents",
    'version': '16.0.1.0.0',
    'summary': 'Integrate MS Sharepoint with Sale Orders',
    'license': 'OEEL-1',
    'author': "Andrius Laukavičius",
    'category': 'Sale/Sale',
    'website': "https://timefordev.com",
    'depends': [
        # odoo
        'sale',
        # oerp-odoo
        'sharepoint_api',
    ],
    'data': [
        'views/sale_order.xml',
        'views/sharepoint_site.xml',
    ],
    'assets': {
        'web.assets_backend': [
            'api_sharepoint/static/src/js/error_dialogs.esm.js',
        ],
    },
    'installable': True,
}
