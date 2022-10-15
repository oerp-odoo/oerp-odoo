# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product HTML Description",
    'version': '15.0.1.1.0',
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
        'security/product_description_html_groups.xml',
        'views/product_template_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
