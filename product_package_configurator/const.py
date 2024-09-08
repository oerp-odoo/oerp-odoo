from enum import Enum


class StrEnum(str, Enum):
    pass


# TODO: add decimal precisions on various float fields!
class DecimalPrecision(StrEnum):
    SIZE = 'Package Configurator Size'


DEFAUL_GLOBAL_BOX_EXTRA = 30  # mm
# Extra size for length and width to compensate, so lid would fit on a
# base!
DEFAULT_LID_EXTRA = 2  # mm
DEFAULT_OUTSIDE_WRAPPING_EXTRA = 20  # mm
MM_TO_SQ_M_COEFFICIENT = 1000000
