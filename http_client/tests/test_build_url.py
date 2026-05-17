from ..utils import build_url
from ..value_objects.request import RelativePath
from . import common


class TestBuildUrl(common.TestHttpClientCommon):
    def test_01_build_url_no_args(self):
        # WHEN
        endpoint = build_url('https://abc.com', RelativePath(pattern='/my_pattern/a'))
        # THEN
        self.assertEqual(endpoint, 'https://abc.com/my_pattern/a')

    def test_02_build_url_with_args(self):
        # WHEN
        endpoint = build_url(
            'https://abc.com',
            RelativePath(pattern='/my_pattern/{}/test/{}', args=('a', 'b')),
        )
        # THEN
        self.assertEqual(endpoint, 'https://abc.com/my_pattern/a/test/b')

    def test_03_build_url_with_args_n_params(self):
        # WHEN
        endpoint = build_url(
            'https://abc.com',
            RelativePath(
                pattern='/my_pattern/{}/test/{}',
                args=('a', 'b'),
                params={'state': 'test', 'active': 'yes'},
            ),
        )
        # THEN
        self.assertEqual(
            endpoint, 'https://abc.com/my_pattern/a/test/b?state=test&active=yes'
        )

    def test_04_build_url_url_with_path(self):
        self.assertEqual(
            build_url(
                'https://abc.com/api',
                RelativePath(pattern='/my_pattern/{}/test/{}', args=('a', 'b')),
            ),
            'https://abc.com/api/my_pattern/a/test/b',
        )
        self.assertEqual(
            build_url('https://abc.com/api', RelativePath(pattern='/my_pattern/a')),
            'https://abc.com/api/my_pattern/a',
        )
        self.assertEqual(
            build_url('https://abc.com/api/', RelativePath(pattern='/my_pattern/a')),
            'https://abc.com/api/my_pattern/a',
        )
        self.assertEqual(
            build_url('https://abc.com/', RelativePath(pattern='/my_pattern/a')),
            'https://abc.com/my_pattern/a',
        )
