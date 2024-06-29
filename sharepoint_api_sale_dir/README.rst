MS Sharepoint API - Sale Directories
####################################

Integrate MS Sharepoint with Sale Orders. It is possible to create/link
sharepoint directory per sale order per partner. For example if on site
you specify ``Sale Directories Root Path`` as ``/Projects``, then for new
sale order called ``SO0001`` and partner called ``P1``, new directory can
be created (initiated via SO). It would be created as a path
``/Projects/P1/SO0001``.

From user perspective, it can open such folders from Odoo sale order.
Folder will be created if it does not exist.

Contributors
============

* Author: Andrius Laukavičius (timefordev)
