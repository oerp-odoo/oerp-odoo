# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Fiscal Position Filter by Company Type",
    'version': '14.0.2.0.0-rc.1',
    'summary': 'Detect fiscal position using partner company type.',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Accounting',
    'depends': [
        'account'
    ],
    'data': [
        'views/account_fiscal_position_views.xml',
    ],
    'installable': True,
}
