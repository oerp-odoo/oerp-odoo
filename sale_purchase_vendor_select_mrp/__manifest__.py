# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE and COPYRIGHT files for details.
{
    "name": "Sale Purchase Select Vendor - MRP",
    "version": "17.0.1.0.0",
    "summary": "Integrate selected Vendor with MRP",
    "license": "LGPL-3",
    "author": "Andrius Laukavičius",
    "website": "https://timefordev.com",
    "category": "Manufacturing/Manufacturing",
    "depends": [
        # odoo
        "sale_purchase_vendor_select",
        "mrp",
    ],
    "installable": False,
    # TODO: set to True once it is installable
    'auto_install': False,
}
