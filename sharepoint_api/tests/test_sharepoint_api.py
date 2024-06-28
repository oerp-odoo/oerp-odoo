import responses

from odoo.addons.http_client.tests.common import CONTENT_TYPE_APPLICATION_JSON

from ..exceptions import MissingSharepointError
from ..model_services.sharepoint_api import PFX_SITE
from .common import TestApiSharepointCommon


class TestSharepointApi(TestApiSharepointCommon):
    @responses.activate
    def test_01_get_site_id_ok(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        endpoint = f'{url}{PFX_SITE}/example.com:/sites/mysite'
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json={'id': 'site-id-123'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.SharepointApi.get_site_id(
            'example.com',
            '/sites/mysite',
            options={'auth': self.sharepoint_auth_1},
        )
        # THEN
        self.assertEqual(res, 'site-id-123')

    @responses.activate
    def test_02_get_site_id_not_found(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        endpoint = f'{url}{PFX_SITE}/example.com:/sites/not-existing-site'
        responses.add(
            responses.GET,
            endpoint,
            status=404,
            json={
                "error": {
                    "code": "itemNotFound",
                    "message": "Requested site could not be found",
                    "innerError": {
                        "date": "2024-06-28T15:14:55",
                        "request-id": "abc-123-456-7890",
                        "client-request-id": "123123-123-123-123-3-2",
                    },
                }
            },
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN, THEN
        with self.assertRaisesRegex(
            MissingSharepointError, r".+Requested site could not be found.+"
        ):
            self.SharepointApi.get_site_id(
                'example.com',
                '/sites/not-existing-site',
                options={'auth': self.sharepoint_auth_1},
            )

    @responses.activate
    def test_03_get_default_drive_id_ok(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        endpoint = f'{url}{PFX_SITE}/site-id-123/drive'
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json={'id': 'drive-id-123'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.SharepointApi.get_default_drive_id(
            'site-id-123',
            options={'auth': self.sharepoint_auth_1},
        )
        # THEN
        self.assertEqual(res, 'drive-id-123')

    @responses.activate
    def test_04_get_directory_ok(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        endpoint = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/root:/my-dir/my-subdir'
        )
        expected_res = {
            "name": "my-subdir",
            "id": "my-subdir-id",
            "webUrl": "https://example.com/sites/my-site/my-dir/my-subdir",
        }
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=expected_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.SharepointApi.get_directory(
            'site-id-123',
            'drive-id-123',
            '/my-dir/my-subdir',
            options={'auth': self.sharepoint_auth_1},
        )
        # THEN
        self.assertEqual(res, expected_res)

    @responses.activate
    def test_05_list_directory_ok(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        endpoint = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/'
            + 'root:/my-dir/my-subdir:/children'
        )
        expected_res = {
            "value": [
                {
                    "name": "f1",
                    "id": "f1-id",
                    "webUrl": "https://example.com/sites/my-site/my-dir/my-subdir/f1",
                },
                {
                    "name": "f2",
                    "id": "f2-id",
                    "webUrl": "https://example.com/sites/my-site/my-dir/my-subdir/f2",
                },
            ]
        }
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=expected_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.SharepointApi.list_directory(
            'site-id-123',
            'drive-id-123',
            '/my-dir/my-subdir',
            options={'auth': self.sharepoint_auth_1},
        )
        # THEN
        self.assertEqual(res, expected_res)

    @responses.activate
    def test_06_create_directory_ok(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        endpoint = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/'
            + 'root:/my-dir/my-subdir:/children'
        )
        expected_res = {
            "name": "f3",
            "id": "f3-id",
            "webUrl": "https://example.com/sites/my-site/my-dir/my-subdir/f3",
        }
        responses.add(
            responses.POST,
            endpoint,
            status=201,
            json=expected_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.SharepointApi.create_directory(
            'site-id-123',
            'drive-id-123',
            '/my-dir/my-subdir',
            {'name': 'f3', "folder": {}},
            options={'auth': self.sharepoint_auth_1},
        )
        # THEN
        self.assertEqual(res, expected_res)
