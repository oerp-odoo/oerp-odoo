Mail Template QWeb View
#######################

Odoo now uses :code:`QWeb` template engine for email content rendering (instead of :code:`Jinja2`), but it uses raw :code:`QWeb`, which does not allow proper inheritance.

This module adds option to choose :code:`QWeb View` engine, where you can specify :code:`QWeb View`. It works similarly as :code:`email_template_qweb` module works for older Odoo versions.

Configuration
=============

Go to :code:`Settings / Technical / Email / Email Templates`, open template and choose :code:`QWeb View` engine and then :code:`QWeb View`.

Contributors
============

* Andrius Laukavičius (Focusate)
