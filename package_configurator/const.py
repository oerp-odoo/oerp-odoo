from enum import Enum


class StrEnum(str, Enum):
    pass


class DecimalPrecision(StrEnum):
    SIZE = 'Package Configurator Size'
    PRICE = 'Package Configurator Price'
    COST = 'Package Configurator Cost'


class ComponentSide(StrEnum):
    INSIDE = 'inside'
    OUTSIDE = 'outside'


class PackageType(StrEnum):
    BOX = 'box'
    INSERT = 'insert'


class SetupType(StrEnum):
    PRODUCTION = 'production'
    PRINT = 'print'
    # Used for both foil and stamps!
    FOIL = 'foil'


class ComponentKind(StrEnum):
    GREYBOARD = 'greyboard'
    CARTON = 'carton'
    WRAPPINGPAPER = 'wrappingpaper'


COMPONENT_SIDE_SELECTION = [
    (ComponentSide.INSIDE, "Inside"),
    (ComponentSide.OUTSIDE, "Outside"),
]

PACKAGE_TYPE_SELECTION = [
    (PackageType.BOX, "Box"),
    (PackageType.INSERT, "Insert"),
]

SETUP_TYPE_SELECTION = [
    (SetupType.PRODUCTION, "Production"),
    (SetupType.PRINT, "Print"),
    (SetupType.FOIL, "Foil"),
]

DEFAUL_GLOBAL_BOX_EXTRA = 30  # mm
# Extra size for length and width to compensate, so lid would fit on a
# base!
DEFAULT_LID_EXTRA = 2  # mm
DEFAULT_OUTSIDE_WRAPPING_EXTRA = 20  # mm
MM_TO_SQ_M_COEFFICIENT = 1000000
