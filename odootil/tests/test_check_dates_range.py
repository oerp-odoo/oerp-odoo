from datetime import datetime

from odoo.exceptions import UserError

from .common import TestOdootilCommon


class TestDatesValidate(TestOdootilCommon):
    """Class to test validation of two dates."""

    def test_01_check_dates_range(self):
        """Test when dates are equal and it is allowed to be equal."""
        try:
            self.Odootil.check_dates_range('2018-01-01', '2018-01-01')
        except UserError:
            self.fail("Should not raise, because dates are allowed to be equal.")

    def test_02_check_dates_range(self):
        """Test when dates are equal and it is not allowed to be equal."""
        with self.assertRaises(UserError):
            self.Odootil.check_dates_range(
                '2018-01-01', '2018-01-01', allow_equal=False
            )

    def test_03_check_dates_range(self):
        """Test when first date is earlier and it is allowed to be equal."""
        try:
            self.Odootil.check_dates_range('2018-01-01', '2018-01-02')
        except UserError:
            self.fail("Should not raise, because first date is earlier.")

    def test_04_check_dates_range(self):
        """Test when first date is earlier, is not allowed to be equal."""
        try:
            self.Odootil.check_dates_range(
                '2018-01-01', '2018-01-02', allow_equal=False
            )
        except UserError:
            self.fail("Should not raise, because first date is earlier.")

    def test_05_check_dates_range(self):
        """Test when second date is earlier and it is allowed to be equal."""
        with self.assertRaises(UserError):
            self.Odootil.check_dates_range('2018-01-02', '2018-01-01')

    def test_06_check_dates_range(self):
        """Test when second date is earlier, is not allowed to be equal."""
        with self.assertRaises(UserError):
            self.Odootil.check_dates_range(
                '2018-01-02', '2018-01-01', allow_equal=False
            )

    def test_07_check_dates_range(self):
        """Test when second date is earlier, date and datetime objects."""
        date_earlier = datetime.strptime('2018.01.02', '%Y.%m.%d')
        date_later = datetime.strptime('2018.01.01', '%Y.%m.%d')
        with self.assertRaises(UserError):
            self.Odootil.check_dates_range(date_earlier, date_later)
        with self.assertRaises(UserError):
            self.Odootil.check_dates_range(date_earlier.date(), date_later.date())
        try:
            self.Odootil.check_dates_range(date_later, date_earlier)
        except UserError:
            self.fail("Should not raise")
