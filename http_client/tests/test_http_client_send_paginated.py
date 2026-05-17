import responses

from ..const import HttpVerb
from ..value_objects.request import RelativePath, RequestInput
from . import common


class TestHttpClientSendPaginated(common.TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )
        cls.auth_1.action_confirm()
        cls.profile_1 = cls.HttpClientProfile.create(
            {
                'name': 'MY-PROFILE-1',
                'base_url': common.DUMMY_URL,
                'auth_id': cls.auth_1.id,
            }
        )

    @responses.activate
    def test_01_client_send_paginated_multi(self):
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
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        response_res = self.HttpClient.send_paginated('next', inp)
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
    def test_02_client_send_paginated_no_links(self):
        # GIVEN
        endpoint_1 = common.DUMMY_ENDPOINT
        responses.add(
            responses.GET,
            endpoint_1,
            status=200,
            json={'a': 10},
        )
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        response_res = self.HttpClient.send_paginated('next', inp)
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, endpoint_1)
        self.assertEqual(len(response_res), 1)
        self.assertEqual(response_res[0].json(), {'a': 10})

    @responses.activate
    def test_03_client_send_paginated_different_key(self):
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
        inp = RequestInput(
            method=HttpVerb.GET,
            relative_path=RelativePath(pattern=common.DUMMY_PATH),
            profile=self.profile_1,
        )
        # WHEN
        response_res = self.HttpClient.send_paginated('next', inp)
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(calls[0].request.url, endpoint_1)
        self.assertEqual(len(response_res), 1)
        self.assertEqual(response_res[0].json(), {'a': 10})
