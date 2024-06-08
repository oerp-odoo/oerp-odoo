# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Units of Measure - Code",
    'version': '15.0.1.1.0',
    'summary': 'Add code field on units of measure',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Sales/Sales',
    'depends': [
        # odoo
        'uom',
    ],
    'data': [
        'data/uom.xml',
        'views/uom_uom_views.xml',
    ],
    'installable': True,
}
