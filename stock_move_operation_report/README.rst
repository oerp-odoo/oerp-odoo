Stock Moves Operation Report
############################

Generates ``CSV`` report to show products moves by source destination locations.

Each row consists of these columns (``in`` means coming into warehouse,
``out`` going out of warehouse):

* product_code: Product Internal Reference
* quantity_start: starting quantity at ``Date Start``.
* manufacture_in: quantity manufactured
* manufacture_out: quantity consumed when manufacturing (e.g. raw material)
* purchase_in:  quantity that was purchased from vendor
* purchase_out: quantity that was returned to vendor
* sell_in: quantity that was returned from customer
* sell_out: quantity that was sold to customer
* inventory_in: custom inventory adjustment (quantity increased in warehouse)
* inventory_out: custom inventory adjustment (quantity decreased in warehouse)
* qunatity_end: ending quantity at ``Date End``.

Usage
=====

Go to ``Inventory / Reporting / Stock Move Operations`` to print report.

Contributors
============

* Andrius Laukavičius (timefordev)
