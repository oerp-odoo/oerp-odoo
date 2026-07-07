# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Repairs Category",
    'version': '19.0.3.0.0',
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
        'views/repair_category.xml',
        'views/repair_order.xml',
    ],
    'installable': True,
}
