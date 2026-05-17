from odoo.exceptions import ValidationError

from odoo.addons.http_client.tests.common import TestHttpClientCommon
from odoo.addons.http_client.value_objects.profile import ProfileFilter


class TestHttpClientProfileGetting(TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.auth_1 = cls.HttpClientAuth.create(
            {
                'name': 'MY-AUTH-1',
            }
        )
        cls.HttpClientProfile.search([]).write({'active': False})
        cls.profile_1 = cls.HttpClientProfile.create(
            {
                'name': 'MY-PROFILE-1',
                'base_url': 'http://example.com',
                'auth_id': cls.auth_1.id,
                'company_id': False,
            }
        )

    def test_01_get_profile_no_filters(self):
        # WHEN
        res = self.HttpClientProfile.get_profile(ProfileFilter())
        # THEN
        self.assertEqual(res, self.profile_1)

    def test_02_get_profile_no_filters_more_than_one(self):
        # GIVEN
        self.profile_1.copy(default={'name': 'MY-PROFILE-2'})
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"More than one profile .+ found matching filter: .+"
        ):
            self.HttpClientProfile.get_profile(ProfileFilter())

    def test_03_get_profile_w_integration(self):
        # GIVEN
        self.profile_1.copy(default={'name': 'MY-PROFILE-2'})
        self.profile_1.integration = 'my_integration_1'
        # WHEN
        res = self.HttpClientProfile.get_profile(
            ProfileFilter(integration='my_integration_1')
        )
        # THEN
        self.assertEqual(res, self.profile_1)

    def test_04_get_profile_w_integration_more_than_one(self):
        # GIVEN
        self.profile_1.integration = 'my_integration_1'
        self.profile_1.copy()
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"More than one profile .+ found matching filter: .+"
        ):
            self.HttpClientProfile.get_profile(
                ProfileFilter(integration='my_integration_1')
            )

    def test_04_get_profile_w_integration_no_matches(self):
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError, r"No profile found matching filter: .+"
        ):
            self.HttpClientProfile.get_profile(
                ProfileFilter(integration='my_integration_2')
            )

    def test_05_get_profile_w_company_id(self):
        # GIVEN
        self.profile_1.copy()
        self.profile_1.company_id = self.company_main.id
        # WHEN
        res = self.HttpClientProfile.get_profile(
            ProfileFilter(company_id=self.company_main.id)
        )
        # THEN
        self.assertEqual(res, self.profile_1)

    def test_06_get_profile_w_company_id_n_integration(self):
        # GIVEN
        self.profile_1.copy(default={'name': 'MY-PROFILE-2'})
        self.profile_1.write(
            {'company_id': self.company_main.id, 'integration': 'my_integration_1'}
        )
        # WHEN
        res = self.HttpClientProfile.get_profile(
            ProfileFilter(
                company_id=self.company_main.id, integration='my_integration_1'
            )
        )
        # THEN
        self.assertEqual(res, self.profile_1)

    def test_07_find_profiles_w_company_id_n_integration(self):
        # GIVEN
        self.profile_1.write(
            {'company_id': self.company_main.id, 'integration': 'my_integration_1'}
        )
        profile_2 = self.profile_1.copy(default={'name': 'MY-PROFILE-2'})
        # WHEN
        res = self.HttpClientProfile.find_profiles(
            ProfileFilter(
                company_id=self.company_main.id, integration='my_integration_1'
            )
        )
        # THEN
        self.assertEqual(res, self.profile_1 | profile_2)
