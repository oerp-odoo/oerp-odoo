MS Sharepoint API
#################

Base integration with MS sharepoint. Provides utilities and setup for Odoo to
communicate with sharepoint API. This module is intended to be used as a base for
specific integrations.

Configuration
=============

To set up authentication go to ``Settings / Technical / Sharepoint / Authentications``.

Expected mandatory settings:

* URL: ``https://graph.microsoft.com``
* Auth Method: ``Bearer``
* Identifier: ``Client ID`` for sharepoint.
* Secret: secret you got when creating app record in sharepoint.
* Grant Type: ``Client Credentials``
* Content Type: ``X WWW Form Urlencoded``
* SCOPE: ``https://graph.microsoft.com/.default`` (could be other depending on your setup)
* Authentication Path Mode: ``Endpoint``
* Authentication Path: ``https://login.microsoftonline.com/{TENANT_ID}/oauth2/v2.0/token``

To set up a site, go to ``Settings / Technical / Sharepoint / Sites``.

Expected mandatory settings:

* Hostname: host name of your sharepoint.
* Site ID
* Drive ID

If you don't know ``Site ID`` or ``Drive ID``, it can be discovered using ``Set Up``
action. For that you have to specify ``Site Relative Path`` (should be something like
/sites/Mysite).

Contributors
============

* Author: Andrius Laukavičius (timefordev)
