from .. import const
from . import common


class TestHttpClientEncoder(common.TestHttpClientCommon):
    def test_01_encode_raw(self):
        self.assertEqual(
            self.HttpClientEncoder.encode({'x': 10, 'y': 20}, const.FORMAT_RAW),
            ({'x': 10, 'y': 20}, None),
        )

    def test_02_encode_json(self):
        self.assertEqual(
            self.HttpClientEncoder.encode({'x': 10}, const.FORMAT_JSON),
            (b'{"x":10}', const.MIMETYPE_JSON),
        )

    def test_03_encode_form(self):
        self.assertEqual(
            self.HttpClientEncoder.encode({'x': 10, 'y': 20}, const.FORMAT_FORM),
            (b'x=10&y=20', const.MIMETYPE_FORM),
        )
