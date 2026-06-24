# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Main Product on Order - Menus",
    'version': '19.0.2.0.0',
    'summary': 'Menus for main product rules views',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'product_main_on_order',
        'sale',
    ],
    'data': [
        'views/menus.xml',
    ],
    'installable': True,
    'auto_install': True,
}
