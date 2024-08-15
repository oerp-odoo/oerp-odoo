import responses

from odoo.addons.http_client.tests.common import (
    CONTENT_TYPE_APPLICATION_JSON,
    DUMMY_URL,
)

from .. import value_objects
from ..exceptions import MissingGithubError
from .common import TestGithubApiCommon

repo_demo = value_objects.Repo(
    name='my-repo',
    owner='my-org',
)


class TestGithubApi(TestGithubApiCommon):
    @responses.activate
    def test_01_list_pulls_wo_query(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/pulls'
        json_res = [
            {
                'url': DUMMY_URL,
                'id': 123456,
                'number': 123,
                'draft': False,
                'head': {
                    'ref': 'some-branch-1',
                    'sha': 'some-commit-sha-1',
                },
                'state': 'open',
                'auto_merge': None,
            },
        ]
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.list_pulls(
            repo_demo,
            options={'auth': self.github_auth_1},
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        headers = calls[0].request.headers
        self.assertEqual(headers['Authorization'], 'Bearer abc123')
        self.assertEqual(headers['Accept'], 'application/vnd.github+json')
        self.assertEqual(headers['X-GitHub-Api-Version'], '2022-11-28')
        self.assertEqual(res, json_res)

    @responses.activate
    def test_02_list_pulls_with_links(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint_1 = f'{url}/repos/my-org/my-repo/pulls'
        endpoint_2 = f'{url}/repos/my-org/my-repo/pulls?per_page=1&page=2'
        responses.add(
            responses.GET,
            endpoint_1,
            status=200,
            json=[
                {
                    'url': DUMMY_URL,
                    'id': 123456,
                    'number': 123,
                    'draft': False,
                    'head': {
                        'ref': 'some-branch-1',
                        'sha': 'some-commit-sha-1',
                    },
                    'state': 'open',
                    'auto_merge': None,
                },
            ],
            headers={
                'Link': f'<{endpoint_2}>; rel="next", <{endpoint_2}>; rel="last"',
                **CONTENT_TYPE_APPLICATION_JSON,
            },
        )
        responses.add(
            responses.GET,
            endpoint_1,
            status=200,
            json=[
                {
                    'url': DUMMY_URL,
                    'id': 22222,
                    'number': 222,
                    'draft': False,
                    'head': {
                        'ref': 'some-branch-2',
                        'sha': 'some-commit-sha-2',
                    },
                    'state': 'open',
                    'auto_merge': None,
                },
            ],
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.list_pulls(
            repo_demo,
            options={'auth': self.github_auth_1},
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0].request.url, endpoint_1)
        self.assertEqual(calls[1].request.url, endpoint_2)
        headers = calls[0].request.headers
        self.assertEqual(headers['Authorization'], 'Bearer abc123')
        self.assertEqual(headers['Accept'], 'application/vnd.github+json')
        self.assertEqual(headers['X-GitHub-Api-Version'], '2022-11-28')
        self.assertEqual(
            res,
            [
                {
                    'url': DUMMY_URL,
                    'id': 123456,
                    'number': 123,
                    'draft': False,
                    'head': {
                        'ref': 'some-branch-1',
                        'sha': 'some-commit-sha-1',
                    },
                    'state': 'open',
                    'auto_merge': None,
                },
                {
                    'url': DUMMY_URL,
                    'id': 22222,
                    'number': 222,
                    'draft': False,
                    'head': {
                        'ref': 'some-branch-2',
                        'sha': 'some-commit-sha-2',
                    },
                    'state': 'open',
                    'auto_merge': None,
                },
            ],
        )

    @responses.activate
    def test_03_list_pulls_w_query_ok(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = (
            f'{url}/repos/my-org/my-repo/pulls?state=open&sort=updated&direction=asc'
        )
        json_res = [
            {
                'url': DUMMY_URL,
                'id': 123456,
                'number': 123,
                'draft': False,
                'head': {
                    'ref': 'some-branch-1',
                    'sha': 'some-commit-sha-1',
                },
                'state': 'open',
                'auto_merge': None,
            }
        ]
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.list_pulls(
            repo_demo,
            params=value_objects.PullParams(sort='updated', direction='asc'),
            options={'auth': self.github_auth_1},
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(res, json_res)

    @responses.activate
    def test_04_list_pulls_404_status_code(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/pulls'
        json_res = [
            {
                'url': DUMMY_URL,
                'id': 123456,
                'number': 123,
                'draft': False,
                'head': {
                    'ref': 'some-branch-1',
                    'sha': 'some-commit-sha-1',
                },
                'state': 'open',
                'auto_merge': None,
            }
        ]
        responses.add(
            responses.GET,
            endpoint,
            status=404,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN, THEN
        with self.assertRaises(MissingGithubError):
            self.GithubApi.list_pulls(
                repo_demo,
                options={'auth': self.github_auth_1},
            )

    @responses.activate
    def test_05_compare_refs(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/compare/master...my-branch-1'
        json_res = {
            'status': 'diverged',
            'ahead_by': 1,
            'behind_by': 2,
            'total_commits': 1,
            'files': [],
        }
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.compare_refs(
            repo_demo, 'master', 'my-branch-1', options={'auth': self.github_auth_1}
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(res, json_res)

    @responses.activate
    def test_06_is_ref_up_to_date_yes(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/compare/master...my-branch-1'
        json_res = {
            'status': 'ahead',
            'ahead_by': 1,
            # If not behind_by, then it is up to date.
            'behind_by': 0,
            'total_commits': 1,
            'files': [],
        }
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.is_ref_up_to_date(
            repo_demo, 'master', 'my-branch-1', options={'auth': self.github_auth_1}
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(res, True)

    @responses.activate
    def test_07_is_ref_up_to_date_no(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/compare/master...my-branch-1'
        json_res = {
            'status': 'diverged',
            'ahead_by': 1,
            # if behind_by, it means not up to date
            'behind_by': 1,
            'total_commits': 1,
            'files': [],
        }
        responses.add(
            responses.GET,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.is_ref_up_to_date(
            repo_demo, 'master', 'my-branch-1', options={'auth': self.github_auth_1}
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        self.assertEqual(res, False)

    @responses.activate
    def test_08_update_pull_head_sha(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/pulls/123/update-branch'
        json_res = {
            'message': 'Updating pull request branch.',
            'url': f'{url}/repos/my-org/my-repo/pulls/123',
        }
        responses.add(
            responses.PUT,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.update_pull(
            repo_demo, 123, options={'auth': self.github_auth_1}
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        body = calls[0].request.body
        self.assertFalse(body)
        self.assertEqual(res, json_res)

    @responses.activate
    def test_09_update_pull_custom_sha(self):
        # GIVEN
        url = self.github_auth_1.url
        endpoint = f'{url}/repos/my-org/my-repo/pulls/123/update-branch'
        json_res = {
            'message': 'Updating pull request branch.',
            'url': f'{url}/repos/my-org/my-repo/pulls/123',
        }
        responses.add(
            responses.PUT,
            endpoint,
            status=200,
            json=json_res,
            headers=CONTENT_TYPE_APPLICATION_JSON,
        )
        # WHEN
        res = self.GithubApi.update_pull(
            repo_demo,
            123,
            expected_head_sha='abcdfegh',
            options={'auth': self.github_auth_1},
        )
        # THEN
        calls = responses.calls
        self.assertEqual(len(calls), 1)
        body = calls[0].request.body
        self.assertEqual(body, b'{"expected_head_sha": "abcdfegh"}')
        self.assertEqual(res, json_res)
