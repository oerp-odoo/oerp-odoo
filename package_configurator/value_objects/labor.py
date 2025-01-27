import dataclasses

from .. import const


@dataclasses.dataclass(frozen=True, kw_only=True)
class Labor:
    name: str
    hour_cost: float
    quantity: int
    # How many components fit on single raw sheet
    fit_qty: int

    @classmethod
    def from_circ(cls, circ, fit_qty: int):
        labor = circ.labor_id
        return cls(
            name=labor.name,
            hour_cost=labor.hour_cost,
            quantity=circ.quantity,
            fit_qty=fit_qty,
        )


@dataclasses.dataclass(frozen=True, kw_only=True)
class LaborProcess:
    name: str
    labor_type: const.LaborType
    units_per_hour: int
    setup_minutes: int
    component_type: const.ComponentType | None = None
    to_fit: bool = False

    @classmethod
    def from_labor_item(
        cls, labor_item, component_type: const.ComponentType | None = None
    ):
        labor_type = labor_item.labor_type_id
        name = labor_item.custom_name or labor_type.name
        return cls(
            name=name,
            labor_type=labor_type.code,
            units_per_hour=labor_item.units_per_hour,
            setup_minutes=labor_item.setup_minutes,
            component_type=component_type,
            to_fit=labor_item.to_fit,
        )
