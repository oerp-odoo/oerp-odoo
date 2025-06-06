# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    'name': 'Manufacturing - Auto Plan',
    'version': '17.0.1.0.0',
    'summary': 'Automatically plan manufacturing after creating it',
    'license': 'LGPL-3',
    'author': 'Andrius Laukavičius',
    'website': 'https://timefordev.com',
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp',
    ],
    'data': ['views/mrp_bom.xml'],
    'installable': True,
}
