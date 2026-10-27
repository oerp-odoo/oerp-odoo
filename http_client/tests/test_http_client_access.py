from odoo import Command

from . import common


class TestHttpClientAccess(common.TestHttpClientCommon):
    """Check multi-company restriction of auth and profile records."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        ResCompany = cls.env['res.company']
        cls.company_1 = ResCompany.create({'name': "HC Company 1"})
        cls.company_2 = ResCompany.create({'name': "HC Company 2"})
        cls.user_system = cls.env['res.users'].create(
            {
                'name': "HC System",
                'login': "hc_system",
                'company_id': cls.company_1.id,
                'company_ids': [Command.set((cls.company_1 | cls.company_2).ids)],
                'group_ids': [Command.set(cls.env.ref('base.group_system').ids)],
            }
        )
        cls.auth_1 = cls.HttpClientAuth.create(
            {'name': "HC-AUTH-1", 'company_id': cls.company_1.id}
        )
        cls.auth_2 = cls.HttpClientAuth.create(
            {'name': "HC-AUTH-2", 'company_id': cls.company_2.id}
        )
        cls.auth_no_company = cls.HttpClientAuth.create(
            {'name': "HC-AUTH-3", 'company_id': False}
        )
        profile_vals = {'base_url': 'http://example.com'}
        cls.profile_1 = cls.HttpClientProfile.create(
            dict(
                profile_vals,
                name="HC-PROFILE-1",
                auth_id=cls.auth_1.id,
                company_id=cls.company_1.id,
            )
        )
        cls.profile_2 = cls.HttpClientProfile.create(
            dict(
                profile_vals,
                name="HC-PROFILE-2",
                auth_id=cls.auth_2.id,
                company_id=cls.company_2.id,
            )
        )
        cls.profile_no_company = cls.HttpClientProfile.create(
            dict(
                profile_vals,
                name="HC-PROFILE-3",
                auth_id=cls.auth_no_company.id,
                company_id=False,
            )
        )

    def _env_with_active_companies(self, companies):
        return self.env(
            user=self.user_system, context={'allowed_company_ids': companies.ids}
        )

    def test_01_auth_search_by_active_companies(self):
        """Auth of a non active company is not visible."""
        # GIVEN
        auths = self.auth_1 | self.auth_2 | self.auth_no_company
        env = self._env_with_active_companies(self.company_1)
        # WHEN
        visible = env['http.client.auth'].search([('id', 'in', auths.ids)])
        # THEN
        self.assertEqual(visible, self.auth_1 | self.auth_no_company)

    def test_02_profile_search_by_active_companies(self):
        """Profile of a non active company is not visible."""
        # GIVEN
        profiles = self.profile_1 | self.profile_2 | self.profile_no_company
        env = self._env_with_active_companies(self.company_2)
        # WHEN
        visible = env['http.client.profile'].search([('id', 'in', profiles.ids)])
        # THEN
        self.assertEqual(visible, self.profile_2 | self.profile_no_company)

    def test_03_search_by_all_active_companies(self):
        """Records of all active companies are visible."""
        # GIVEN
        env = self._env_with_active_companies(self.company_1 | self.company_2)
        # WHEN
        auths = env['http.client.auth'].search(
            [('id', 'in', (self.auth_1 | self.auth_2 | self.auth_no_company).ids)]
        )
        # THEN
        self.assertEqual(auths, self.auth_1 | self.auth_2 | self.auth_no_company)
