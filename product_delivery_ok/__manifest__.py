# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product Delivery Field",
    'version': '15.0.1.0.0',
    'summary': 'Field to mark if product is used for delivery',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Product/Delivery',
    'depends': [
        # odoo
        'product',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
}
