Sale Extra Statuses
###################

Show extra statuses on sale orders:

Purchase Status:

* RFC (if any of related purchases is not yet confirmed)
* Confirmed (If all purchase orders are confirmed)
* Received (If all stock (from purchases) is received in "input" location). Only used
  when Incoming Shipments have two steps (input+stock).
* Done (If all stock is received to warehouse).

Production Progress:

* Empty if no related manufacturing orders.
* Percentage how many manufacturing orders are completed out of total.

Contributors
------------

* Author: Andrius Laukavičius (timefordev)
