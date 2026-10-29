from . import common


class TestHttpClientAuthDisplayName(common.TestHttpClientCommon):
    def test_01_display_name_with_name(self):
        auth = self.HttpClientAuth.create({'name': 'MY-AUTH-1'})
        self.assertEqual(auth.display_name, 'MY-AUTH-1')

    def test_02_display_name_without_name(self):
        auth = self.HttpClientAuth.create({'base_url': 'http://127.0.0.1'})
        self.assertEqual(auth.display_name, f'({auth.id}) http://127.0.0.1')
