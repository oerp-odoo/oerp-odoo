MRP Production Split - Extended
###############################

When manufacturing order is split that is tracked by serial number,
usually it is expected to mass produce serials, so splitting MOs per
single quantity before doing mass produce, makes it impossible to use
mass produce serials. For this, we allow to use any split method with
serial numbers, so it would be possible to use odoo standard split
for serial numbers during mass produce of serial numbers.

Also, adding an option to force default split mode.

Contributors
============

* Andrius Laukavičius (timefordev)
