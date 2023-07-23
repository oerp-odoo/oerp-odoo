# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "MRP Serial Numbers Import",
    'version': '15.0.1.0.0',
    'summary': 'mrp, serial number, import, file',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Manufacturing/Manufacturing',
    'depends': [
        # odoo
        'mrp',
    ],
    'data': [
        'wizards/stock_assign_serial_views.xml',
    ],
    'demo': [
        'demo/product_product.xml',
        'demo/mrp_bom.xml',
    ],
    'installable': False,
}
