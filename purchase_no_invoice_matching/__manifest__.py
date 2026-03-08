# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Purchase - No Invoice Matching",
    "version": "17.0.1.0.0",
    "summary": "Allows to disable auto matching between purchase and vendor bills",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Inventory/Purchase",
    "depends": [
        # odoo
        "purchase",
    ],
    "installable": True,
    "data": [
        "views/res_config_settings.xml",
    ],
}
