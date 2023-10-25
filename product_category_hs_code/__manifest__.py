# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Category - HS Code",
    'version': '16.0.1.0.0',
    'summary': 'HS Code on product category',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Delivery',
    'depends': [
        # odoo
        'delivery',
    ],
    'data': ['views/product_category.xml'],
    'installable': True,
    'auto_install': True,
}
