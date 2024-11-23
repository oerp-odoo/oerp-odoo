Purchase - Grouping
###################

When purchase is about to be created via procurement (e.g. sale order confirmation),
it is possible to choose how to group it:

* No grouping: it will not try to find existing purchase RFQ to merge it with. Instead
  it will always create new one.
* By Root Procurement Group: all purchases will be matched by their root procurement, so
  only those will have same purchase order (e.g. multiple level BOM purchase procurements
  of the same sale order). Important! For this to work, ``Buy`` rule, must have
  ``Propagation of Procurement Group`` set to ``Propagate``!

Configuration
=============

Go to ``Purchase / Configuration / Settings / Orders`` and select ``Grouping``.

NOTE. Currently when enabled this only works for all products per company.

Contributors
------------

* Author: Andrius Laukavičius (timefordev)
