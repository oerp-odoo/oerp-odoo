from odoo.tests.common import TransactionCase

from ..tools.coord import get_nearest_coord

COORD_VILNIUS = (54.6892, 25.2798)
COORD_WARSAW = (52.2297, 21.0122)
COORD_BERLIN = (52.5200, 13.4050)
COORD_PARIS = (48.8566, 2.3522)

# 13m from COORD_BERLIN
COORD_BERLIN_NEAREST = (52.520100, 13.405100)
# 60m from COORD_BERLIN
COORD_BERLIN_MEDIUM = (52.520500, 13.406000)
# 130m from COORD_BERLIN
COORD_BERLIN_FARTHEST = (52.521000, 13.407000)


class TestNearestCoord(TransactionCase):
    def test_01_get_nearest_coord_from_vilnius(self):
        self.assertEqual(
            get_nearest_coord(
                COORD_VILNIUS,
                [COORD_PARIS, COORD_BERLIN, COORD_WARSAW],
                radius_m=5000000,
            ),
            COORD_WARSAW,
        )

    def test_02_get_nearest_coord_from_paris(self):
        self.assertEqual(
            get_nearest_coord(
                COORD_PARIS,
                [COORD_VILNIUS, COORD_BERLIN, COORD_WARSAW],
                radius_m=5000000,
            ),
            COORD_BERLIN,
        )

    def test_03_get_nearest_coord_self_candidate(self):
        self.assertEqual(
            get_nearest_coord(
                COORD_PARIS,
                [COORD_PARIS, COORD_VILNIUS, COORD_BERLIN, COORD_WARSAW],
                radius_m=5000000,
            ),
            COORD_PARIS,
        )

    def test_04_get_nearest_coord_match_very_close_coords(self):
        self.assertEqual(
            get_nearest_coord(
                COORD_BERLIN,
                [COORD_BERLIN_MEDIUM, COORD_BERLIN_FARTHEST, COORD_BERLIN_NEAREST],
                radius_m=1000,
            ),
            COORD_BERLIN_NEAREST,
        )

    def test_05_get_nearest_coord_no_match_by_bounded(self):
        self.assertEqual(
            get_nearest_coord(
                COORD_VILNIUS, [COORD_PARIS, COORD_BERLIN, COORD_WARSAW], radius_m=10
            ),
            None,
        )

    def test_06_get_nearest_coord_no_match_by_haversine(self):
        self.assertEqual(
            get_nearest_coord(
                COORD_BERLIN,
                [COORD_BERLIN_MEDIUM, COORD_BERLIN_FARTHEST, COORD_BERLIN_NEAREST],
                radius_m=1,
                max_distance_m=1,
            ),
            None,
        )
