import dataclasses


@dataclasses.dataclass(frozen=True, kw_only=True)
class BaseDimensions:
    length: float  # mm
    width: float
    height: float
    outside_wrapping_extra: float


@dataclasses.dataclass(frozen=True, kw_only=True)
class LidDimensions:
    height: float
    thickness: float
    # To make it slightly bigger than base so it would fit on it.
    extra: float


@dataclasses.dataclass(frozen=True, kw_only=True)
class Layout2D:
    """Package layout on 2D plane."""

    length: float  # mm
    width: float

    @property
    def area(self):
        return self.length * self.width
