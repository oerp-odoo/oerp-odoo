# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Package Configurator",
    'version': '17.0.1.1.0',
    'summary': 'Base package product configurator module',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'security/product_package_configurator_groups.xml',
        'security/ir.model.access.csv',
        'security/package_configurator_box_security.xml',
        'security/package_configurator_box_circulation_security.xml',
        'security/package_box_type_security.xml',
        'security/package_carton_security.xml',
        'security/package_wrappingpaper_security.xml',
        'security/package_lamination_security.xml',
        'data/decimal_precision.xml',
        'views/res_config_settings.xml',
        'views/package_box_type.xml',
        'views/package_carton.xml',
        'views/package_wrappingpaper.xml',
        'views/package_lamination.xml',
        'views/package_configurator_box.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}
