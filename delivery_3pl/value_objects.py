from __future__ import annotations

import dataclasses
from collections.abc import Callable

from odoo.addons.sale.models.sale_order import SaleOrder
from odoo.addons.sale.models.sale_order_line import SaleOrderLine


@dataclasses.dataclass(frozen=True, kw_only=True)
class IntegrationSpec:
    label: str
    sale_events: SaleEvents
    is_3pl_line: Callable[[SaleOrderLine], bool]
    use_non_ok_exception: bool = False


@dataclasses.dataclass(frozen=True, kw_only=True)
class SaleEvents:
    on_confirm: Callable[[SaleOrder], dict]
    on_cancel: Callable[[SaleOrder], dict] | None = None
    on_sync_shipment_status: Callable[[SaleOrder], dict]
    on_draft: Callable[[SaleOrder], dict] | None = None
