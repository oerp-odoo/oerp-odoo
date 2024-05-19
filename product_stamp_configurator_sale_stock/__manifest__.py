# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Stamp Configurator - Inventory",
    'version': '16.0.1.0.0',
    'summary': 'Stamp product configurator integration with inventory',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Inventory',
    'depends': [
        'sale_stock',
        # oerp-odoo
        'product_stamp_configurator_sale',
    ],
    'installable': False,
    'data': [
        'views/res_config_settings.xml',
    ],
}
