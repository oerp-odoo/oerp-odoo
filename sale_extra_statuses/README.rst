Sale Extra Statuses
###################

Show extra statuses on sale orders:

Purchase Status:

* RFC (if any of related purchases is not yet confirmed)
* Confirmed (If all purchase orders are confirmed)
* Received (If all stock (from purchases) is received in "input" location). Only used
  when Incoming Shipments have two steps (input+stock).
* Done (If all stock is received to warehouse).

Delivery Progress:

* Empty if no related delivery orders (pickings).
* Percentage how many delivery orders are completed out of total (
  that are delivering to customer).

Production Progress:

* Empty if no related manufacturing orders.
* Percentage how many manufacturing orders are completed out of total.

Component Progress:

* Empty if no related manufacturing orders.
* Percentage how many manufacturing orders have all components available. Also if some
  components are unavailable, progress will have either yellow or red color. Yellow
  means that Sale Order Delivery Date is later than all manufacturing Start Dates.
  Red means one of the dates are not set or any manufacturing Start Date is later than
  Sale Order Delivery Date.

Contributors
------------

* Author: Andrius Laukavičius (timefordev)
