# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Define used server machines",
    'version': '1.0.1',
    'summary': 'Define used server machines per partner',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Extra Tools',
    'depends': [
        'mail'
    ],
    'external_dependencies': {'python': ['footil']},
    'images': [
        'static/description/machine_instance.png',
    ],
    'data': [
        'security/machine_security.xml',
        'security/ir.model.access.csv',
        'data/machine_cpu_data.xml',
        'data/machine_dbs_data.xml',
        'data/machine_os_data.xml',
        'data/mail_template_data.xml',
        'views/machine_menus.xml',
        'views/machine_instance_views.xml',
        'views/machine_group_views.xml',
        'views/machine_tag_views.xml',
        'views/machine_cpu_views.xml',
        'views/machine_os_views.xml',
        'views/machine_dbs_views.xml',
        'views/res_partner_views.xml',
        'wizards/machine_email_views.xml',
    ],
    'demo': [
        'demo/machine_cpu_demo.xml',
        'demo/machine_instance_demo.xml',
        'demo/machine_group_demo.xml',
    ],
    'application': True,
}
