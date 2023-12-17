# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Stamp Configurator - Intrastat",
    'version': '16.0.1.0.0',
    'summary': 'Stamp product configurator integration with intrastat',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Accounting/Accounting',
    'depends': [
        # odoo
        'account_intrastat',
        # oerp-odoo
        'product_stamp_configurator',
    ],
    'installable': True,
    'data': [
        'views/res_config_settings.xml',
        'wizards/stamp_configure_views.xml',
    ],
}
