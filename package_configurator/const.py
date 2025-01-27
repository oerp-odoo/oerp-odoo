from enum import Enum


class StrEnum(str, Enum):
    pass


class DecimalPrecision(StrEnum):
    SIZE = 'Package Configurator Size'
    PRICE = 'Package Configurator Price'
    COST = 'Package Configurator Cost'
    MEASURE = 'Package Configurator Measure'


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


class ComponentType(StrEnum):
    BASE = 'base'
    LID = 'lid'
    BASE_WRAPPINGPAPER_INSIDE = 'base_wrappingpaper_inside'
    BASE_WRAPPINGPAPER_OUTSIDE = 'base_wrappingpaper_outside'
    LID_WRAPPINGPPAER_INSIDE = 'lid_wrappingpaper_inside'
    LID_WRAPPINGPPAER_OUTSIDE = 'lid_wrappingpaper_outside'


class LaborType(StrEnum):
    # generic type means, its not tied specifically to configurator options
    # (e.g. foiling, lamination), so it can be applied whenever you want.
    GENERIC = 'generic'
    WRAPPINGPAPER_CLADDING = 'wrappingpaper_cladding'
    LAMINATION = 'lamination'
    FOILING = 'foiling'
    # Labor cost for making insert.
    INSERT_PUTTING = 'insert_putting'
    # Laber cost for fitting it in a box.
    INSERT_FORMATION = 'insert_formation'


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
HELP_NO_LIMIT = "0 means no limit"
DEFAUL_GLOBAL_PACKAGE_EXTRA = 30  # mm
# Extra size for length and width to compensate, so lid would fit on a
# base!
DEFAULT_LID_EXTRA = 2  # mm
DEFAULT_OUTSIDE_WRAPPING_EXTRA = 20  # mm
MM_TO_SQ_M_COEFFICIENT = 1000000
