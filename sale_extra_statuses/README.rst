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
  means that components are arriving before production starts.
  Red means that components are either arriving late (after production is started) or
  not arriving at all.

Contributors
------------

* Author: Andrius Laukavičius (timefordev)
