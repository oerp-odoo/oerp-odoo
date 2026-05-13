# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    'name': 'Odoo Utilities',
    'version': '19.0.4.0.0',
    'summary': 'odoo, utilities, helper methods',
    'license': 'LGPL-3',
    'author': 'Andrius Laukavičius',
    'website': 'https://timefordev.com',
    'category': 'Hidden/Tools',
    'depends': [
        # odoo
        'web',
    ],
    'external_dependencies': {
        'python': ['footil', 'num2words', 'validators', 'email_validator']
    },
    'data': [
        'security/ir.model.access.csv',
    ],
    'installable': True,
}
