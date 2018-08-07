# -*- coding: utf-8 -*-
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
        'base'
    ],
    'data': [
        'security/machine_security.xml',
        # 'security/ir.model.access.csv',
        'data/machine_data.xml',
        'views/machine_menus.xml',
        'views/machine_instance_views.xml',
        'views/machine_cpu_views.xml',
    ],
    'demo': [
        'demo/machine_cpu_demo.xml',
    ],
    'application': True,
}
