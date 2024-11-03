import dataclasses

from .. import const


@dataclasses.dataclass(frozen=True, kw_only=True)
class BoxComponentType:
    """Specification describing box component.

    Attributes:
        name: unique name identifying component
        label: user friendly name
        scope: to which types of sheets this component type can be used.

    """

    name: str
    label: str
    scope: const.SheetTypeScope

    @classmethod
    def from_default(cls):
        return cls(
            name="",
            label="",
            scope=const.SheetTypeScope.GREYBOARD,
        )
