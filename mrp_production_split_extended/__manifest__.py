# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP Production Split - Extended",
    'version': '15.0.1.0.0',
    'summary': 'Extra changes for production split',
    'license': 'AGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp_production_split',
    ],
    'data': [
        'views/res_config_settings_views.xml',
        'wizards/mrp_production_split_wizard_views.xml',
    ],
    'installable': True,
}
