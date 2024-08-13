Github API
##########

Base integration with Github. Provides utilities and setup for Odoo to
communicate with Github API. This module is intended to be used as a base for
specific integrations.

Configuration
=============

To set up authentication go to ``Settings / Technical / Github / Authentications``.

Expected mandatory settings:

* URL: ``https://api.github.com``
* Auth Method: ``Bearer``
* Identifier: Keep it empty.
* Secret: Github token (can be personal access token with appropriate scopes, depending
  on specific integration needs).
* Grant Type: Keep it empty

To set up a repository, go to ``Settings / Technical / Github / Repositories``.

Expected mandatory settings:

* Name: name of the repository.
* Owner: github organization or github user name
* Auth: authentication record to use.

Contributors
============

* Author: Andrius Laukavičius (timefordev)
