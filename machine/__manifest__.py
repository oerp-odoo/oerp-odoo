# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Define used server machines",
    'version': '0.1.0',
    'summary': 'Define used server machines per partner',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://github.com/oerp-odoo",
    'category': 'Extra Tools',
    'depends': [
        'mail'
    ],
    'data': [
        'security/machine_security.xml',
        'security/ir.model.access.csv',
        'data/machine_cpu_data.xml',
        'data/machine_dbs_data.xml',
        'data/machine_os_data.xml',
        'views/machine_menus.xml',
        'views/machine_instance_views.xml',
        'views/machine_tag_views.xml',
        'views/machine_cpu_views.xml',
        'views/machine_os_views.xml',
        'views/machine_dbs_views.xml',
        'views/res_partner_views.xml',
    ],
    'demo': [
        'demo/machine_cpu_demo.xml',
        'demo/machine_instance_demo.xml',
    ],
    'application': True,
}
