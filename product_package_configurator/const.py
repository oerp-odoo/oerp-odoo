from enum import Enum


class StrEnum(str, Enum):
    pass


class DecimalPrecision(StrEnum):
    SIZE = 'Package Configurator Size'


DEFAULT_LID_THICKNESS = 1.5  # mm
# Extra size for length and width to compensate, so lid would fit on a
# base!
DEFAULT_LID_EXTRA = 2  # mm
DEFAULT_OUTSIDE_WRAPPING_EXTRA = 20  # mm
