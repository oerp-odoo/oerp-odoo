# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Website - Remove Default Social Links",
    "version": "15.0.1.0.0",
    "summary": "Website default social (fake) links are removed",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Website/Website",
    "depends": [
        # odoo
        "website",
    ],
    "data": ["templates/website_footer.xml"],
    "installable": True,
    "auto_install": True,
}
