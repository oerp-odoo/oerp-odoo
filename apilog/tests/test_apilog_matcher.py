from odoo.addons.odootil.value_objects.http import HttpVerb

from .. import value_objects as vo
from . import common


class TestApilogMatcher(common.TestApilogCommon):
    def test_01_log_matcher_match_by_endpoint_part(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path', verb=HttpVerb.GET, status_code=200
        )
        # WHEN
        res = self.ApilogMatcher.match("'/my/path' in inp.endpoint", inp)
        # THEN
        self.assertEqual(res, True)

    def test_02_log_matcher_match_by_endpoint_part_re(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path', verb=HttpVerb.GET, status_code=200
        )
        # WHEN
        res = self.ApilogMatcher.match("re_match(r'.+/my/path$', inp.endpoint)", inp)
        # THEN
        self.assertEqual(res, True)

    def test_03_log_matcher_not_match_by_endpoint_part(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/other/path',
            verb=HttpVerb.GET,
            status_code=200,
        )
        # WHEN
        res = self.ApilogMatcher.match("'/my/path' in inp.endpoint", inp)
        # THEN
        self.assertEqual(res, False)

    def test_04_log_matcher_match_by_status_code(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path', verb=HttpVerb.GET, status_code=200
        )
        # WHEN
        res = self.ApilogMatcher.match("inp.status_code == 200", inp)
        # THEN
        self.assertEqual(res, True)

    def test_05_log_matcher_not_match_by_status_code(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path', verb=HttpVerb.GET, status_code=401
        )
        # WHEN
        res = self.ApilogMatcher.match("inp.status_code == 200", inp)
        # THEN
        self.assertEqual(res, False)

    def test_06_log_matcher_match_by_verb(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path', verb=HttpVerb.GET, status_code=200
        )
        # WHEN
        res = self.ApilogMatcher.match("inp.verb == 'GET'", inp)
        # THEN
        self.assertEqual(res, True)

    def test_07_log_matcher_not_match_by_verb(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path', verb=HttpVerb.GET, status_code=200
        )
        # WHEN
        res = self.ApilogMatcher.match("inp.verb == 'POST'", inp)
        # THEN
        self.assertEqual(res, False)

    def test_08_log_matcher_match_by_call_stack(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            status_code=200,
            call_stack=(('A', 'my_method'), ('B', 'my_method')),
        )
        # WHEN
        res = self.ApilogMatcher.match("('A', 'my_method') in inp.call_stack", inp)
        # THEN
        self.assertEqual(res, True)

    def test_09_log_matcher_not_match_by_call_stack(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            status_code=200,
            call_stack=(('A', 'my_method'), ('B', 'my_method')),
        )
        # WHEN
        res = self.ApilogMatcher.match("('A', 'my_method') not in inp.call_stack", inp)
        # THEN
        self.assertEqual(res, False)

    def test_10_log_matcher_match_by_auth_fingerprint(self):
        # GIVEN
        inp = vo.ApilogMatcherInput(
            endpoint='http://localhost/my/path',
            verb=HttpVerb.GET,
            status_code=200,
            auth_fingerprint="abc123",
        )
        # WHEN
        res = self.ApilogMatcher.match("'abc123' in inp.auth_fingerprint", inp)
        # THEN
        self.assertEqual(res, True)
