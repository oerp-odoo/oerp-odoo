# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Main Product on Order - Menus",
    'version': '15.0.1.0.0',
    'summary': 'Menus for main product rules views',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'product_main_on_order',
        'sale',
    ],
    'data': [
        'views/menus.xml',
    ],
    'installable': False,
    'auto_install': True,
}
