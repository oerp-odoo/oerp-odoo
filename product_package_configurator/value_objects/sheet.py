from __future__ import annotations

import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class SheetQuantity:
    items: list[SheetQuantityItem]
    min_qty: int = 0


@dataclasses.dataclass(frozen=True, kw_only=True)
class SheetQuantityItem:
    code: str
    fit_qty: int
