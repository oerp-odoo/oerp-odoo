# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery HS Code per Country",
    'version': '15.0.2.0.0-rc.1',
    'summary': 'delivery, harmonized code, origin country, countries',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Warehouse',
    'depends': [
        # odoo
        'delivery',
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
    'installable': False,
}
