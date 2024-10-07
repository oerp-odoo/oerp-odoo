# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Sale - Unique Number",
    "version": "15.0.1.0.0",
    "summary": "Make sale number unique per company.",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Sales/Sales",
    "depends": [
        # odoo
        "sale",
    ],
    "data": ["views/res_config_settings_views.xml"],
    "installable": True,
}
