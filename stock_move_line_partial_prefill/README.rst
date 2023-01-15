Partially Prefill Detailed Operations
#####################################

Adds :code:`Partially Pre-fill Detailed Operations` field on operation types.
If set, when picking is confirmed, detailed operations will be filled using
``Operations`` information (using demand information and not reserved info).

This can be useful, when tracking by serial is used on products and serial
numbers are scanned. So before doing that, all other necessary data is already
filled.

Currently only ``Delivery`` operation types are supported.

This feature only works if ``Operation Type`` ``Reservation Method`` is set to
``Manually`` and ``Show Detailed Operations`` options is checked as well.

Contributors
============

* Andrius Laukavičius (timefordev)
