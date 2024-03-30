Basic HTTP Authentication
#########################

Add Basic HTTP Authentication method where :code:`username:password` is encoded in base64 format.

Authentication expects this kind of header: :code:`AUTHORIZATION: Basic [b64]`, which is RFC 7617 standard.

This method was inspired by module :code:`auth_api_key`.

**NOTE**. When creating Basic Auth records, make sure username/password pair is unique to not make it possible to find multiple records with same credentials.

Constraint can't be added, because :code:`username` and :code:`password` values are also allowed to be retrieved from server environment.

Configuration
=============

To use this type of authentication, with admin user (debug mode enabled), go to :code:`Settings / Technical / Authentication / Basic`. Create new record, specifying its :code:`Name` (unique identifier), :code:`User` (Odoo user that will be actually authorized access. User must have admin access) :code:`Username` and :code:`Password`.

If you want to take credentials from server environment, :code:`Username` and :code:`Password` can be left empty. Check :code:`server_environment` module for details how it works.

Contributors
============

* Andrius Laukavičius (timefordev)
