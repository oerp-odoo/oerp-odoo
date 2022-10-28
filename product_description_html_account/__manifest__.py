# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Product HTML Description - Invoices",
    'version': '15.0.1.0.0',
    'summary': 'Can specify Invoices HTML description for product',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'account',
        # oerp-odoo
        'product_description_html',
    ],
    'data': [
        'views/product_template_views.xml',
    ],
    'installable': True,
    'auto_install': True,
}
