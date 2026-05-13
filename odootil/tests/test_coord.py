from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase

from ..tools.coord import form_coord_string, parse_dd_coord


class TestCoord(TransactionCase):
    def test_01_parse_dd_coord_correct(self):
        self.assertEqual(parse_dd_coord('1, 1'), (1, 1))
        self.assertEqual(parse_dd_coord(' 1, 1 ', clean_whitespace=True), (1, 1))
        self.assertEqual(parse_dd_coord('-1,-1'), (-1, -1))
        self.assertEqual(parse_dd_coord('1,-1'), (1, -1))
        self.assertEqual(parse_dd_coord('-1, 1'), (-1, 1))
        self.assertEqual(parse_dd_coord('4.5343, 5.23132'), (4.5343, 5.23132))
        self.assertEqual(parse_dd_coord('4.5343, -5.23132'), (4.5343, -5.23132))
        self.assertEqual(parse_dd_coord('-4.5343, 5.23132'), (-4.5343, 5.23132))
        self.assertEqual(parse_dd_coord('1, 5.63234'), (1, 5.63234))
        self.assertEqual(parse_dd_coord('1, -5.63234'), (1, -5.63234))
        self.assertEqual(parse_dd_coord('-1, -5.63234'), (-1, -5.63234))
        self.assertEqual(parse_dd_coord('-1, 5.63234'), (-1, 5.63234))
        self.assertEqual(parse_dd_coord('-90, -180'), (-90, -180))
        self.assertEqual(parse_dd_coord('-90, -180'), (-90, -180))
        self.assertEqual(parse_dd_coord('-89.999, -179.999'), (-89.999, -179.999))
        self.assertEqual(parse_dd_coord('89.999, 179.999'), (89.999, 179.999))
        self.assertEqual(parse_dd_coord('1 1', delimiter=' '), (1, 1))
        self.assertEqual(
            parse_dd_coord(' 1 1 ', delimiter=' ', clean_whitespace=True), (1, 1)
        )
        self.assertEqual(parse_dd_coord('-1 -1', delimiter=' '), (-1, -1))
        self.assertEqual(parse_dd_coord('1 -1', delimiter=' '), (1, -1))
        self.assertEqual(parse_dd_coord('-1 1', delimiter=' '), (-1, 1))
        self.assertEqual(
            parse_dd_coord('4.5343 5.23132', delimiter=' '), (4.5343, 5.23132)
        )
        self.assertEqual(
            parse_dd_coord('4.5343 -5.23132', delimiter=' '), (4.5343, -5.23132)
        )
        self.assertEqual(
            parse_dd_coord('-4.5343 5.23132', delimiter=' '), (-4.5343, 5.23132)
        )
        self.assertEqual(parse_dd_coord('1 5.63234', delimiter=' '), (1, 5.63234))
        self.assertEqual(parse_dd_coord('1 -5.63234', delimiter=' '), (1, -5.63234))
        self.assertEqual(parse_dd_coord('-1 -5.63234', delimiter=' '), (-1, -5.63234))
        self.assertEqual(parse_dd_coord('-1 5.63234', delimiter=' '), (-1, 5.63234))
        self.assertEqual(parse_dd_coord('-90 -180', delimiter=' '), (-90, -180))
        self.assertEqual(parse_dd_coord('-90 -180', delimiter=' '), (-90, -180))
        self.assertEqual(
            parse_dd_coord('-89.999 -179.999', delimiter=' '), (-89.999, -179.999)
        )
        self.assertEqual(
            parse_dd_coord('89.999 179.999', delimiter=' '), (89.999, 179.999)
        )

    def test_02_parse_dd_coord_wrong_type(self):
        msg = r"Coordinate values must be float or int! .+"
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('abc, abc')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1, abc')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('abc, 1')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('abc abc', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1 abc', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('abc 1', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1,1 1,1', delimiter=' ')

    def test_03_parse_dd_coord_wrong_values_number(self):
        msg = r"Coordinate must consist of exactly two values! .+"
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('abc')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('abc', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1.5')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1 1 1', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1,, 1 ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord(' 1, 1, ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord(', 1, 1')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1, 1, 1')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1,1 1,1')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1 1 ', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord(' 1 1 ', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord(' 1 1', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1  1', delimiter=' ', clean_whitespace=True)
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1.5', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('1,1', delimiter=' ')

    def test_04_parse_dd_coord_wrong_range(self):
        msg = (
            r"Latitude range must be between -90 and \+90\. "
            + r"Longitude between -180 and \+180! .+"
        )
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('-91, 50.4')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('91, 50.4')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('90, -181')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('90, 181')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('91, 181')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('-91 50.4', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('91 50.4', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('90 -181', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('90 181', delimiter=' ')
        with self.assertRaisesRegex(ValidationError, msg):
            parse_dd_coord('91 181', delimiter=' ')

    def test_05_form_coord_string_as_string_input(self):
        self.assertEqual(form_coord_string('1', '2'), '1, 2')

    def test_06_form_coord_string_as_int_input(self):
        self.assertEqual(form_coord_string(1, 2), '1, 2')

    def test_07_form_coord_string_as_float_input(self):
        self.assertEqual(form_coord_string(1.0, 2.0), '1.0, 2.0')
