Unique Product Code
###################

Makes product code unique globally (no company) and locally (per company). We include archived products also when validating constraint.

NOTE. Standard odoo also checks whether same code exists, but it does not prevent user
from creating duplicates (that check is also bypassed when importing products).

Configuration
=============

A new configuration field ``Unique Product Codes`` in General Settings for enabling/disabling product's code uniqueness:

* ``Disabled`` - uniqueness is disabled;
* ``Enabled`` - enabled case-sensitive uniqueness;
* ``Enabled Case-Insensitive`` - enabled case-insensitive uniqueness;

Contributors
============

* Andrius Laukavičius (timefordev)
