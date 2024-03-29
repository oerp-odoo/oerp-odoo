# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Repairs Category",
    'version': '15.0.2.0.0',
    'summary': 'Use categories to distinguish different type of repairs',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Maintenance',
    'depends': [
        # odoo
        'repair',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/repair_category_security.xml',
        'views/repair_category_views.xml',
        'views/repair_order_views.xml',
    ],
    'installable': True,
}
