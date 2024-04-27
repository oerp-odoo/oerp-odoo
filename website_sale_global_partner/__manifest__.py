# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "eCommerce - Global Partner",
    'version': '15.0.1.0.0',
    'summary': 'eCommerce global partner',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Website/Website',
    'depends': [
        # odoo
        'website_sale',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
