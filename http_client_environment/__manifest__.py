# Author: Andrius Laukavičius. Copyright: Andrius Laukavičius.
# See LICENSE file for full copyright and licensing details.
{
    'name': "HTTP Client with server environment",
    'version': '16.0.2.0.0',
    'summary': 'Store some auth fields on server environment',
    'license': 'OEEL-1',
    'author': "Andrius Laukavičius",
    'website': "https://timefordev.com",
    'depends': [
        # oca-server-env
        'server_environment',
        # base-toc
        'http_client',
    ],
    'installable': True,
}
