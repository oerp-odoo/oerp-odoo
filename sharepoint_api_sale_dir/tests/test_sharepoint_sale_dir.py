import responses

from odoo.addons.http_client.tests.common import CONTENT_TYPE_APPLICATION_JSON
from odoo.addons.sharepoint_api.model_services.sharepoint_api import PFX_SITE
from odoo.addons.sharepoint_api.tests.common import TestApiSharepointCommon


class TestSharepointSaleDir(TestApiSharepointCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.SaleOrder = cls.env['sale.order']
        cls.ResPartner = cls.env['res.partner']
        cls.SharepointSaleDir = cls.env['sharepoint.sale.dir']
        cls.partner_1 = cls.ResPartner.create({'name': 'P1', 'is_company': True})
        cls.sale_1 = cls.SaleOrder.create({'partner_id': cls.partner_1.id})
        cls.sharepoint_site_1 = cls.SharepointSite.create(
            {
                'hostname': 'example.com',
                'auth_id': cls.sharepoint_auth_1.id,
                'site_id': 'site-id-123',
                'drive_id': 'drive-id-123',
                'site_rel_path': '/sites/mysite',
                'sale_dir_root_path': '/mydocs',
                'company_id': cls.company_main.id,
                'state': 'confirm',
            }
        )

    def test_01_get_site_ok(self):
        # WHHEN
        site = self.SharepointSite.get_site(self.company_main, sale_dir=True)
        # THEN
        self.assertEqual(site, self.sharepoint_site_1)

    def test_02_get_site_missing_sale_dir_root_path(self):
        # GIVEN
        self.sharepoint_site_1.sale_dir_root_path = False
        # WHHEN
        site = self.SharepointSite.get_site(self.company_main, sale_dir=True)
        # THEN
        self.assertFalse(site)

    @responses.activate
    def test_03_action_open_sharepoint_directory_not_exist(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        # To check if dir exists
        endpoint_check_dir = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/root:'
            + f'/mydocs/P1/{self.sale_1.name}'
        )
        responses.add(
            responses.GET,
            endpoint_check_dir,
            status=404,
            json={'error': 'not_found'},
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # To create dir
        endpoint_create_dir = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/root:/mydocs/P1:/children'
        )
        web_url = f"https://example.com/sites/my-site/mydocs/P1/{self.sale_1.name}"
        responses.add(
            responses.POST,
            endpoint_create_dir,
            status=201,
            json={
                "name": self.sale_1.name,
                "id": "some-id",
                "webUrl": web_url,
            },
        )
        # WHEN
        res = self.sale_1.action_open_sharepoint_directory()
        # THEN
        responses.assert_call_count(endpoint_check_dir, 1)
        responses.assert_call_count(endpoint_create_dir, 1)
        self.assertEqual(
            res,
            {
                'type': 'ir.actions.act_url',
                'url': web_url,
                'target': 'new',
            },
        )
        self.assertEqual(self.sale_1.sharepoint_sale_dir_url, web_url)

    @responses.activate
    def test_04_action_open_sharepoint_directory_exist_sharepoint_only(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        # To check if dir exists
        endpoint_check_dir = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/root:'
            + f'/mydocs/P1/{self.sale_1.name}'
        )
        web_url = f"https://example.com/sites/my-site/mydocs/P1/{self.sale_1.name}"
        responses.add(
            responses.GET,
            endpoint_check_dir,
            status=200,
            json={
                "name": self.sale_1.name,
                "id": "some-id",
                "webUrl": web_url,
            },
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # To create dir
        endpoint_create_dir = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/root:/mydocs/P1:/children'
        )
        responses.add(
            responses.POST,
            endpoint_create_dir,
            status=201,
            json={
                "name": self.sale_1.name,
                "id": "some-id",
                "webUrl": web_url,
            },
        )
        # WHEN
        res = self.sale_1.action_open_sharepoint_directory()
        # THEN
        responses.assert_call_count(endpoint_check_dir, 1)
        responses.assert_call_count(endpoint_create_dir, 0)
        self.assertEqual(
            res,
            {
                'type': 'ir.actions.act_url',
                'url': web_url,
                'target': 'new',
            },
        )
        self.assertEqual(self.sale_1.sharepoint_sale_dir_url, web_url)

    @responses.activate
    def test_05_action_open_sharepoint_directory_exist_internally(self):
        # GIVEN
        url = self.sharepoint_auth_1.url
        # To check if dir exists
        endpoint_check_dir = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/root:'
            + f'/mydocs/P1/{self.sale_1.name}'
        )
        web_url = f"https://example.com/sites/my-site/mydocs/P1/{self.sale_1.name}"
        self.sale_1.sharepoint_sale_dir_url = web_url
        responses.add(
            responses.GET,
            endpoint_check_dir,
            status=200,
            json={
                "name": self.sale_1.name,
                "id": "some-id",
                "webUrl": web_url,
            },
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # To create dir
        endpoint_create_dir = (
            f'{url}{PFX_SITE}/site-id-123/drives/drive-id-123/'
            + f'root:/mydocs/P1/{self.sale_1.name}'
        )
        responses.add(
            responses.POST,
            endpoint_create_dir,
            status=201,
            json={
                "name": self.sale_1.name,
                "id": "some-id",
                "webUrl": web_url,
            },
        )
        # WHEN
        res = self.sale_1.action_open_sharepoint_directory()
        # THEN
        responses.assert_call_count(endpoint_check_dir, 0)
        responses.assert_call_count(endpoint_create_dir, 0)
        self.assertEqual(
            res,
            {
                'type': 'ir.actions.act_url',
                'url': web_url,
                'target': 'new',
            },
        )
        self.assertEqual(self.sale_1.sharepoint_sale_dir_url, web_url)
