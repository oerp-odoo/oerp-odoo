from odoo.addons.http_client.tests.common import TestHttpClientCommon


class TestGithubApiCommon(TestHttpClientCommon):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.GithubAuth = cls.env['github.auth']
        cls.GithubApi = cls.env['github.api']
        cls.github_auth_1 = cls.create_auth(
            vals=dict(auth_method='bearer', secret='abc123')  # nosec: B106
        )
        cls.github_auth_1.action_confirm()

    @classmethod
    def get_auth_model(cls):
        return cls.GithubAuth
