Delivery Custom QWeb Email Templates
####################################

Rewrites existing Delivery email templates using :code:`QWeb` with few changes:

* User signature is not forced, because this email is intended to be detached from specific user.

Configuration
=============

To activate new templates (instead of old ones written with :code:`Jinja2`), go to :code:`Settings / Technical / Email / Templates`, open :code:`Transfer` standard template and change :code:`Body templating engine` to :code:`QWeb`.

Contributors
============

* Andrius Laukavičius (Focusate)
