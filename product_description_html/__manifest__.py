# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product HTML Description",
    'version': '15.0.1.3.0',
    'summary': 'Can specify HTML description for product',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Product/Sale',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': False,
}
