# Author: Andrius Laukavičius. Copyright: JSC Focusate.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Common Note",
    'version': '12.0.1.0.0',
    'summary': 'Common note that can use company data.',
    'license': 'OEEL-1',
    'author': "Focusate",
    'website': "http://www.focusate.eu",
    'category': 'Extra Tools',
    'depends': [
        # odoo
        'base',
    ],
    'data': [
        'views/res_company_views.xml',
    ],
    'installable': True,
}
