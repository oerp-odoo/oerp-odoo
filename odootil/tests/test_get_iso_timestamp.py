from datetime import datetime

from odoo.fields import Datetime

from .common import TestOdootilCommon


class TestContextTimestampIso(TestOdootilCommon):
    """Class to test validation of two dates."""

    @classmethod
    def setUpClass(cls):
        """Set up record with tz context."""
        super().setUpClass()
        cls.Partner_tz = cls.ResPartner.with_context(tz='Lithuania/Vilnius')

    def test_01_context_timestamp_iso(self):
        """Test with datetime as string."""
        dt = Datetime.context_timestamp_iso(self.Partner_tz, '2018-01-31 10:15:20')
        self.assertEqual(
            dt,
            '2018-01-31T10:15:20+00:00',
            "Incorrect datetime ISO format returned.",
        )

    def test_02_context_timestamp_iso(self):
        """Test with date as string."""
        dt = Datetime.context_timestamp_iso(self.Partner_tz, '2018-01-31')
        self.assertEqual(
            dt,
            '2018-01-31T00:00:00+00:00',
            "Incorrect datetime ISO format returned.",
        )

    def test_03_context_timestamp_iso(self):
        """Test with datetime object."""
        dt = datetime.strptime('2018.01.31 10:15:20', '%Y.%m.%d %H:%M:%S')
        dt = Datetime.context_timestamp_iso(self.Partner_tz, dt)
        self.assertEqual(
            dt,
            '2018-01-31T10:15:20+00:00',
            "Incorrect datetime ISO format returned.",
        )

    def test_04_context_timestamp_iso(self):
        """Test with date object."""
        dt = datetime.strptime('2018.01.31 10:15:20', '%Y.%m.%d %H:%M:%S').date()
        dt = Datetime.context_timestamp_iso(self.Partner_tz, dt)
        self.assertEqual(
            dt,
            '2018-01-31T00:00:00+00:00',
            "Incorrect datetime ISO format returned.",
        )
