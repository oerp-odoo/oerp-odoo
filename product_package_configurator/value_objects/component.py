import dataclasses

from .. import const


@dataclasses.dataclass(frozen=True, kw_only=True)
class BoxComponentType:
    """Specification describing box component.

    Attributes:
        name: unique name identifying component
        label: user friendly name

    """

    name: str
    label: str
    scope: const.SheetTypeScope
    # TODO: these should be removed once layout calculations are moved to component
    # model!
    length_field: str
    width_field: str

    @classmethod
    def from_default(cls):
        return cls(
            name="",
            label="",
            scope=const.SheetTypeScope.GREYBOARD,
            length_field="",
            width_field="",
        )
