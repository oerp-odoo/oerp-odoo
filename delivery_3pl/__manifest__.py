# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Delivery - 3PL",
    'version': '19.0.1.0.0',
    'summary': 'Helper module to integrate Odoo with 3PL platforms',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Delivery',
    'depends': [
        # odoo
        'stock_delivery',
        # oerp-odoo
        'http_client',
    ],
    'data': [
        'security/ir.model.access.csv',
        'security/tpl_service_security.xml',
        'data/ir_cron.xml',
        'views/menus.xml',
        'views/tpl_service.xml',
        'views/sale_order.xml',
    ],
    'installable': True,
}
