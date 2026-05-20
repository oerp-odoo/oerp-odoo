from __future__ import annotations

import json
import math
from functools import lru_cache

import haversine

from odoo import _
from odoo.exceptions import ValidationError
from odoo.tools import LazyTranslate

from .. import const

_lt = LazyTranslate(__name__, default_lang='en_US')


def parse_dd_coord(
    coord: str, delimiter=',', clean_whitespace=False, error_prefix=None
) -> tuple[float | int, float | int]:
    """Validate Decimal Degrees format coordinate.

    Checks whether coordinate is correct:

    * First part must be latitude
    * Second part must be longitude
    * Latitude value must be between -90 and +90
    * Longitude value must be between -180 and +180

    Arguments:
        coord: coordinate to validate
        delimiter: symbol latitude and longitude are separated.
        clean_whitespace: clean whitespace before validating coordinates.
        error_prefix: whether to add error prefix text before actual error.

    """

    def normalize(val: float):
        if val.is_integer():
            return int(val)
        return val

    def format_error(msg):
        if error_prefix:
            return _(error_prefix, msg)
        return msg

    if clean_whitespace:
        coord = coord.strip()
    parts = coord.split(delimiter)
    # Using translation function, but this is not gonna work, because
    # odoo needs to find an env!
    suffix = _lt(
        f" Input: coord='{coord}', delimiter='{delimiter}', "
        + f"clean_whitespace='{clean_whitespace}'"
    )
    if len(parts) != 2:
        raise ValidationError(
            format_error(_lt("Coordinate must consist of exactly two values!") + suffix)
        )
    try:
        latitude = float(parts[0].strip())
        longitude = float(parts[1].strip())
    except ValueError:
        raise ValidationError(
            format_error(_lt("Coordinate values must be float or int!") + suffix)
        )
    lat_lower, lat_upper = const.LATITUDE_LOWER_BOUND, const.LATITUDE_UPPER_BOUND
    long_lower, long_upper = const.LONGITUDE_LOWER_BOUND, const.LONGITUDE_UPPER_BOUND
    if not (
        lat_lower <= latitude <= lat_upper and long_lower <= longitude <= long_upper
    ):
        raise ValidationError(
            format_error(
                _lt(
                    "Latitude range must be between %(lat_lower)s and +%(lat_upper)s. "
                    + "Longitude between %(long_lower)s and +%(long_upper)s!%(suffix)s",
                    lat_lower=lat_lower,
                    lat_upper=lat_upper,
                    long_lower=long_lower,
                    long_upper=long_upper,
                    suffix=suffix,
                )
            )
        )
    return (normalize(latitude), normalize(longitude))


def form_coord_string(
    latitude: str | int | float, longitude: str | int | float, delimiter=', '
):
    return delimiter.join((str(latitude), str(longitude)))


def parse_route_coordinates_expr(
    route_coordinates: str, check_missing=False, error_prefix=''
):
    """Parse and validate route coordinates expression.

    '[["1.1", "1.2"], ["1.3", "1.4"]]' -> [["1.1", "1.2"], ["1.3", "1.4"]]
    """

    def validate_coords(coords_list):
        # A bit too defensive checks, but these can be entered by
        # user manually, so we should be careful what we allow!
        exc = ValidationError(_(msg, comment))
        if not isinstance(coords_list, list):
            raise exc
        # It must have at least two coordinates!
        if check_missing and len(coords_list) < 2:
            raise exc
        for coord in coords_list:
            if not isinstance(coord, list) or len(coord) != 2:
                raise exc
            latitude, longitude = coord[0], coord[1]
            if not isinstance(latitude, str) or not isinstance(longitude, str):
                raise exc
            if (
                not check_missing
                and latitude == const.UNKNOWN
                and longitude == const.UNKNOWN
            ):
                continue
            parse_dd_coord(form_coord_string(latitude, longitude), error_prefix=msg)

    msg = f"{error_prefix}Incorrect Route Coordinates Syntax: %s"
    comment = _lt(
        "Coordinates must be a list of two pair list strings! Minimum of"
        + " two coordinates are required!"
    )
    coords = route_coordinates
    try:
        coords_list = json.loads(coords)
    except Exception as e:
        raise ValidationError(_(msg, e))
    validate_coords(coords_list)
    return coords_list


def get_nearest_coord(
    src_coord: tuple[float, float],
    candidate_coords: list[tuple[float, float]],
    radius_m: float,
    max_distance_m=float("inf"),
) -> tuple[float, float] | None:
    """Find the nearest coordinate from candidates to source."""
    src_lat, src_lon = src_coord
    delta_lat, delta_lon = _get_bounding_box_delta_lat_lon(
        src_lat, radius_m / const.METERS_IN_KM
    )
    nearest = None
    for candidate_coord in candidate_coords:
        lat, lon = candidate_coord
        # Bounding box to filter far away coordinates fast. It is faster
        # to do this operation (on very far away coords than calculating haversine)
        if abs(lat - src_lat) > delta_lat:
            continue
        if abs(lon - src_lon) > delta_lon:
            continue
        distance = haversine.haversine(
            (src_lat, src_lon), (lat, lon), unit=haversine.Unit.METERS
        )
        if distance < max_distance_m:
            max_distance_m = distance
            nearest = candidate_coord
    return nearest


@lru_cache(maxsize=1000)
def _get_bounding_box_delta_lat_lon(
    latitude: float,
    radius_km: float,
) -> tuple[float, float]:
    delta_lat = radius_km / const.KM_PER_DEGREE_LATITUDE
    delta_lon = radius_km / (
        const.KM_PER_DEGREE_LATITUDE * math.cos(math.radians(latitude))
    )
    return (delta_lat, delta_lon)
