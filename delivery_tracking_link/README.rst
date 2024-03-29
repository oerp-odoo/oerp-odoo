Custom Delivery Tracking Links
##############################

Allows to generate links for deliveries that have no specific provider. Defined URL Format then is combined with related picking :code:`Tracking Reference`.

URLs can use :code:`picking` object placeholder. E.g. :code:`https://some-domain.com/tracking/{picking.carrier_tracking_ref}` would generate tracking link using tracking number from picking.

NOTE. These links are only used for carriers with :code:`Provider` selected as :code:`Fixed Price` or :code:`Based on Rules`. If carrier has specific provider, its own tracking link implementation will be used instead (or if some other module implements tracking link for mentioned providers, those then will also take priority).

Can also use ``Custom Tracking URL`` on picking, to directly specify link
without any extra rules.

NOTE. If you are using ``Custom Tracking URL``, ``cancel_shipment`` won't unset
custom URL, because that method relies on specific carrier integration and this
URL does not rely on any of that.

Configuration
-------------

To create delivery links, go to :code:`Inventory / Configuration / Delivery / Tracking Links`.

Contributors
============

* Andrius Laukavičius (timefordev)
