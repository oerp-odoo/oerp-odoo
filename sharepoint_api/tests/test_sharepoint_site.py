import responses

from odoo.exceptions import ValidationError

from odoo.addons.http_client.tests.common import CONTENT_TYPE_APPLICATION_JSON

from ..model_services.sharepoint_api import PFX_SITE
from .common import TestApiSharepointCommon


class TestSharepointSite(TestApiSharepointCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.sharepoint_site_1 = cls.SharepointSite.create(
            {
                'hostname': 'example.com',
                'auth_id': cls.sharepoint_auth_1.id,
                'site_rel_path': '/sites/mysite',
                'company_id': cls.company_main.id,
            }
        )

    def test_01_get_site_ok(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {
                'site_id': 'site-id-123',
                'drive_id': 'drive-id-123',
                'state': 'confirm',
            }
        )
        # WHHEN
        site = self.SharepointSite.get_site(self.company_main)
        # THEN
        self.assertEqual(site, self.sharepoint_site_1)

    def test_02_get_site_not_confirmed(self):
        # WHHEN
        site = self.SharepointSite.get_site(self.company_main)
        # THEN
        self.assertFalse(site)

    @responses.activate
    def test_01_action_setup_missing_all(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        responses.add(
            responses.GET,
            f'{url}{PFX_SITE}/example.com:/sites/mysite',
            status=200,
            json={'id': 'site-id-123'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        responses.add(
            responses.GET,
            f'{url}{PFX_SITE}/site-id-123/drive',
            status=200,
            json={'id': 'drive-id-123'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.sharepoint_site_1.action_setup_missing()
        # THEN
        self.assertEqual(res, True)
        self.assertEqual(self.sharepoint_site_1.site_id, 'site-id-123')
        self.assertEqual(self.sharepoint_site_1.drive_id, 'drive-id-123')

    @responses.activate
    def test_02_action_setup_missing_site_id_only(self):
        # GIVEN
        self.sharepoint_site_1.drive_id = 'drive-id-234'
        url = self.sharepoint_auth_1.url
        responses.add(
            responses.GET,
            f'{url}{PFX_SITE}/example.com:/sites/mysite',
            status=200,
            json={'id': 'site-id-123'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.sharepoint_site_1.action_setup_missing()
        # THEN
        self.assertEqual(res, True)
        self.assertEqual(self.sharepoint_site_1.site_id, 'site-id-123')
        self.assertEqual(self.sharepoint_site_1.drive_id, 'drive-id-234')

    @responses.activate
    def test_03_action_setup_missing_drive_id_only(self):
        # GIVEN
        self.sharepoint_site_1.site_id = 'site-id-234'
        url = self.sharepoint_auth_1.url
        responses.add(
            responses.GET,
            f'{url}{PFX_SITE}/site-id-234/drive',
            status=200,
            json={'id': 'drive-id-123'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.sharepoint_site_1.action_setup_missing()
        # THEN
        self.assertEqual(res, True)
        self.assertEqual(self.sharepoint_site_1.site_id, 'site-id-234')
        self.assertEqual(self.sharepoint_site_1.drive_id, 'drive-id-123')

    @responses.activate
    def test_04_action_setup_missing_nothing(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {
                'site_id': 'site-id-234',
                'drive_id': 'drive-id-234',
            }
        )
        # WHEN
        res = self.sharepoint_site_1.action_setup_missing()
        # THEN
        self.assertEqual(res, True)
        self.assertEqual(self.sharepoint_site_1.site_id, 'site-id-234')
        self.assertEqual(self.sharepoint_site_1.drive_id, 'drive-id-234')

    @responses.activate
    def test_05_action_setup_missing_site_rel_path_not_set(self):
        # GIVEN
        self.sharepoint_site_1.write({'site_rel_path': False})
        # WHEN
        with self.assertRaisesRegex(
            ValidationError, r"Site Relative Path is needed to discover Site ID"
        ):
            self.sharepoint_site_1.action_setup_missing()
        # THEN

    def test_06_action_confirm_ok(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {
                'site_id': 'site-id-123',
                'drive_id': 'drive-id-123',
            }
        )
        # WHEN
        self.sharepoint_site_1.action_confirm()
        # THEN
        self.assertEqual(self.sharepoint_site_1.state, 'confirm')

    def test_07_action_confirm_missing_site_id(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {
                'drive_id': 'drive-id-123',
            }
        )
        # WHEN
        with self.assertRaisesRegex(
            ValidationError, r"Site ID must be set to confirm site!"
        ):
            self.sharepoint_site_1.action_confirm()

    def test_08_action_confirm_missing_drive_id(self):
        # GIIVEN
        self.sharepoint_site_1.write(
            {
                'site_id': 'site-id-123',
            }
        )
        # WHEN
        with self.assertRaisesRegex(
            ValidationError, r"Drive ID must be set to confirm site!"
        ):
            self.sharepoint_site_1.action_confirm()

    def test_07_action_to_draft_from_confirm(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {'site_id': 'site-id-123', 'drive_id': 'drive-id-123', 'state': 'confirm'}
        )
        # WHEN
        self.sharepoint_site_1.action_to_draft()
        # THEN
        self.assertEqual(self.sharepoint_site_1.state, 'draft')

    def test_08_action_to_draft_from_cancel(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {'site_id': 'site-id-123', 'drive_id': 'drive-id-123', 'state': 'cancel'}
        )
        # WHEN
        self.sharepoint_site_1.action_to_draft()
        # THEN
        self.assertEqual(self.sharepoint_site_1.state, 'draft')

    def test_09_action_to_cancel_from_confirm(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {'site_id': 'site-id-123', 'drive_id': 'drive-id-123', 'state': 'confirm'}
        )
        # WHEN
        self.sharepoint_site_1.action_cancel()
        # THEN
        self.assertEqual(self.sharepoint_site_1.state, 'cancel')

    def test_10_action_to_cancel_from_draft(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {'site_id': 'site-id-123', 'drive_id': 'drive-id-123', 'state': 'draft'}
        )
        # WHEN
        self.sharepoint_site_1.action_cancel()
        # THEN
        self.assertEqual(self.sharepoint_site_1.state, 'cancel')

    def test_10_check_unique_site_company_id(self):
        # GIVEN
        self.sharepoint_site_1.write(
            {'site_id': 'site-id-123', 'drive_id': 'drive-id-123', 'state': 'confirm'}
        )
        site_2 = self.sharepoint_site_1.copy()
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"Confirmed Site must be unique per company!"
        ):
            site_2.action_confirm()
