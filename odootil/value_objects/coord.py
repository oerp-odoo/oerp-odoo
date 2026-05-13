import dataclasses
import json

from ..const import UNKNOWN


@dataclasses.dataclass(frozen=True)
class Coordinate:
    latitude: str
    longitude: str

    def to_tuple(self) -> tuple[str, str]:
        return (self.latitude, self.longitude)

    def to_tuple_float(self) -> tuple[float, float]:
        return (float(self.latitude), float(self.longitude))

    @classmethod
    def to_coordinates(cls, coordinates_expr: str) -> list["Coordinate"]:
        """Create list of Coordinate objects from JSON list of coordinates expr."""
        coords_list = json.loads(coordinates_expr)
        res = []
        for coord in coords_list:
            res.append(cls(latitude=coord[0], longitude=coord[1]))
        return res

    @classmethod
    def as_unknown(cls):
        return cls(latitude=UNKNOWN, longitude=UNKNOWN)
