# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Define used server machines",
    'version': '15.0.2.0.0',
    'summary': 'Define used server machines per partner',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Machines/Machines',
    'depends': [
        # odoo
        'mail',
    ],
    'external_dependencies': {'python': ['footil', 'validators']},
    'images': [
        'static/description/machine_instance.png',
    ],
    'data': [
        'security/machine_groups.xml',
        'security/ir.model.access.csv',
        'security/machine_instance_security.xml',
        'data/machine_cpu.xml',
        'data/machine_dbs.xml',
        'data/machine_os.xml',
        'data/mail_template.xml',
        'views/machine_menus.xml',
        'views/machine_instance_views.xml',
        'views/machine_group_views.xml',
        'views/machine_tag_views.xml',
        'views/machine_cpu_views.xml',
        'views/machine_os_views.xml',
        'views/machine_dbs_views.xml',
        'views/res_partner_views.xml',
        'views/res_config_settings_views.xml',
        'wizards/machine_email_views.xml',
    ],
    'demo': [
        'demo/machine_cpu.xml',
        'demo/machine_instance.xml',
        'demo/machine_group.xml',
    ],
    'application': True,
    'installable': True,
}
