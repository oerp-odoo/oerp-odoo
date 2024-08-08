# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Unique Product Code",
    'version': '17.0.1.0.0',
    'summary': 'product, code, unique',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
