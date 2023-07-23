# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Email Marketing Contact Extra Fields",
    'version': '15.0.1.0.0',
    'summary': 'mailing list, contacts, fields',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Marketing/Email Marketing',
    'depends': [
        # odoo
        'mass_mailing',
    ],
    'data': [
        'security/mass_mailing_contacts_fields_groups.xml',
        'data/res_groups.xml',
        'views/mailing_contact_views.xml',
        'views/res_config_settings_views.xml',
    ],
    'installable': False,
}
