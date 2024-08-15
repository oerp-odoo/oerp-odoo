import responses

from . import common


class TestCallFollowLinks(common.TestHttpClientCommon):
    @responses.activate
    def test_01_call_http_method_follow_links_multi(self):
        # GIVEN
        endpoint_1 = common.DUMMY_ENDPOINT
        endpoint_2 = f'{common.DUMMY_ENDPOINT}?page=2'
        endpoint_3 = f'{common.DUMMY_ENDPOINT}?page=3'
        responses.add(
            responses.GET,
            endpoint_1,
            status=200,
            json={'a': 10},
            headers={'Link': f'<{endpoint_2}>; rel="next", <{endpoint_3}>; rel="last"'},
        )
        responses.add(
            responses.GET,
            endpoint_2,
            status=200,
            json={'b': 20},
            headers={'Link': f'<{endpoint_3}>; rel="next", <{endpoint_3}>; rel="last"'},
        )
        responses.add(
            responses.GET,
            endpoint_3,
            status=200,
            json={'c': 30},
        )
        # WHEN
        response_res = self.HttpClientController.call_http_method_follow_links(
            'next',
            'get',
            options={'endpoint': endpoint_1},
        )
        calls = responses.calls
        self.assertEqual(len(calls), 3)
        self.assertEqual(calls[0].request.url, endpoint_1)
        self.assertEqual(calls[1].request.url, endpoint_2)
        self.assertEqual(calls[2].request.url, endpoint_3)
        self.assertEqual(len(response_res), 3)
        self.assertEqual(response_res[0].json(), {'a': 10})
        self.assertEqual(response_res[1].json(), {'b': 20})
        self.assertEqual(response_res[2].json(), {'c': 30})

    @responses.activate
    def test_02_call_http_method_follow_links_no_links(self):
        # GIVEN
        endpoint_1 = common.DUMMY_ENDPOINT
        responses.add(
            responses.GET,
            endpoint_1,
            status=200,
            json={'a': 10},
        )
        # WHEN
        response_res = self.HttpClientController.call_http_method_follow_links(
            'next',
            'get',
            options={'endpoint': endpoint_1},
        )
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, endpoint_1)
        self.assertEqual(len(response_res), 1)
        self.assertEqual(response_res[0].json(), {'a': 10})

    @responses.activate
    def test_03_call_http_method_follow_links_different_key(self):
        # GIVEN
        endpoint_1 = common.DUMMY_ENDPOINT
        endpoint_2 = f'{common.DUMMY_ENDPOINT}?page=2'
        responses.add(
            responses.GET,
            endpoint_1,
            status=200,
            json={'a': 10},
            headers={'Link': f'<{endpoint_2}>; rel="upcoming"'},
        )
        # WHEN
        response_res = self.HttpClientController.call_http_method_follow_links(
            'next',
            'get',
            options={'endpoint': endpoint_1},
        )
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, endpoint_1)
        self.assertEqual(len(response_res), 1)
        self.assertEqual(response_res[0].json(), {'a': 10})
