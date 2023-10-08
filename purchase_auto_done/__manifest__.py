# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "Purchase - Auto Lock",
    'version': '15.0.1.0.0',
    'summary': 'Automatically lock purchase order on fully paid/received ',
    'license': 'LGPL-3',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'category': 'Inventory/Purchase',
    'depends': [
        # odoo
        'purchase_stock',
    ],
    'data': [
        'views/res_config_settings_views.xml',
    ],
    'installable': True,
}
