# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Reordering Rules Without Upper Date",
    "version": "17.0.1.0.0",
    "summary": "Schedule reordering rules ignoring scheduled upper date",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Inventory",
    "depends": [
        # odoo
        "stock",
    ],
    "data": ["views/res_config_settings.xml"],
    "installable": True,
}
