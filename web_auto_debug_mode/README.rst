Developer Mode on Login
=======================

Allows to automatically enable developer (debug) mode when logging in.
This option is enabled by default for admin user.

This is alternative module for :code:`developer_mode` module.

Differences:

* This module is auto installed (can be useful when developing and need
    to recreate databases often).
* By default sets :code:`?debug` for admin user when logging in
    (original one by default only sets for root user, which you can't
    log in directly on Odoo 12).
* Uses simpler implementation, without a need to fully override (and
    overwrite) :code:`web_login` method.
* Feature is managed via user settings, not via access groups.

Contributors
------------

* Andrius Laukavičius (timefordev)
