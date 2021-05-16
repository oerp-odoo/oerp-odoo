# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery HS Code per Country",
    'version': '12.0.1.0.0',
    'summary': 'delivery, harmonized code, origin country, countries',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Warehouse',
    'depends': [
        'delivery_hs_code'
    ],
    'data': [
        'security/ir.model.access.csv',
        'views/product_template_views.xml',
    ],
}
