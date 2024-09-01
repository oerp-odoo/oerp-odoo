# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Package Configurator",
    'version': '17.0.1.0.0',
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
        'security/package_box_type_security.xml',
        'security/package_carton_security.xml',
        'data/decimal_precision.xml',
        'views/package_box_type.xml',
        'views/package_carton.xml',
        'views/package_configurator_box.xml',
        'views/menus.xml',
    ],
    'application': True,
    'installable': True,
}
