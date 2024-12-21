# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "MRP - Optional Tracking",
    "version": "15.0.1.0.0",
    "summary": "Optionally Track serials/lots on manufacturing",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Manufacturing/Manufacturing",
    "depends": [
        # odoo
        "mrp",
    ],
    "data": ["views/product_template_views.xml"],
    "installable": True,
}
