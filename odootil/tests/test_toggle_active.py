from ..mixins.odootil_toggle_active import _filter_xml_ids
from .common import TestOdootilCommon

DUMMY_XML_IDS = ['x.abc1', 'x.abc2', 'y.abc3', 'y.abc4', 'z.abc5']


class TestToggleActive(TestOdootilCommon):
    """Test odootil.toggle_active mixin."""

    def test_01_filter_xml_ids(self):
        """Filter xml_ids without filter."""
        res = _filter_xml_ids(DUMMY_XML_IDS)
        self.assertEqual(res, DUMMY_XML_IDS)

    def test_02_filter_xml_ids(self):
        """Filter xml_ids with 'x' module filter."""
        res = _filter_xml_ids(DUMMY_XML_IDS, modules=['x'])
        self.assertEqual(res, ['x.abc1', 'x.abc2'])

    def test_03_filter_xml_ids(self):
        """Filter xml_ids with ['x, y'] module filter."""
        res = _filter_xml_ids(DUMMY_XML_IDS, modules=['x', 'y'])
        self.assertEqual(res, ['x.abc1', 'x.abc2', 'y.abc3', 'y.abc4'])

    def test_04_filter_xml_ids(self):
        """Filter xml_ids with ['y, x'] module filter."""
        res = _filter_xml_ids(DUMMY_XML_IDS, modules=['y', 'x'])
        self.assertEqual(res, ['x.abc1', 'x.abc2', 'y.abc3', 'y.abc4'])

    def test_05_filter_xml_ids(self):
        """Filter xml_ids with ['NONE'], to filter all."""
        res = _filter_xml_ids(DUMMY_XML_IDS, modules=['NONE'])
        self.assertEqual(res, [])
