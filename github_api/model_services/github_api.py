import dataclasses
import logging

from odoo import api, models
from odoo.exceptions import ValidationError

from odoo.addons.http_client.models.http_client_controller import _raise_endpoint_error
from odoo.addons.http_client.value_objects import PathItem

from ..exceptions import MissingGithubError
from ..value_objects import PullParams, Repo

_logger = logging.getLogger(__name__)


PATH_PULLS = '{pfx}/pulls'
PATH_COMPARE = '{pfx}/compare/{ref1}...{ref2}'
PATH_UPDATE_BRANCH = '{path_pulls}/{pull_number}/update-branch'
EXTRA_HEADERS = {
    'Accept': 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
}


class GithubApi(models.AbstractModel):
    """Model to communicate with Github API."""

    _name = 'github.api'
    _inherit = 'http.client.controller'
    _description = "Github API"
    _auth_model = 'github.auth'

    def list_pulls(
        self, repo: Repo, params: PullParams | None = None, options=None
    ) -> dict:
        """Return Github site ID.

        options are used to provide extra request options, like auth.
        """
        if options is None:
            options = {}
        path = PATH_PULLS.format(pfx=repo.pfx_path)
        options['path_item'] = PathItem(
            path_expression=path, params=dataclasses.asdict(params) if params else None
        )
        options = self._prepare_request_options(path, options=options)
        # Listing pull requests can return paginated response, so we might
        # need to call multiple links to get all the data.
        responses_ = self.call_http_method_follow_links('next', 'get', options=options)
        result = []
        for response in responses_:
            result.extend(response.json())
        return result

    def compare_refs(self, repo: Repo, ref1: str, ref2: str, options=None) -> dict:
        """Compare two git references."""
        path = PATH_COMPARE.format(pfx=repo.pfx_path, ref1=ref1, ref2=ref2)
        return self._call_github_http_method('get', path, options=options).json()

    def is_ref_up_to_date(self, repo: Repo, ref1: str, ref2: str, options=None) -> bool:
        """Check whether ref2 is up to date to ref1.

        Up to date means that ref2 has everything ref1 has.
        """
        res = self.compare_refs(repo, ref1, ref2, options=options)
        return not res['behind_by']

    def update_pull(
        self,
        repo: Repo,
        pull_number: int,
        expected_head_sha: str | None = None,
        options=None,
    ):
        """Update pull request rebasing target branch on it.

        Args:
            repo: repository data object.
            pull_number: the number that identifies the pull request
            expected_head_sha: The expected SHA of the pull request's
            HEAD ref. This is the most recent commit on the pull
                request's branch. If the expected SHA does not match the
                pull request's HEAD, you will receive a 422
                Unprocessable Entity status. If not set, will use
                SHA of the pull request's current HEAD ref.
            options: extra options

        """
        path = PATH_UPDATE_BRANCH.format(
            path_pulls=PATH_PULLS.format(pfx=repo.pfx_path),
            pull_number=pull_number,
        )
        payload = None
        if expected_head_sha:
            payload = {'expected_head_sha': expected_head_sha}
        return self._call_github_http_method(
            'put', path, payload=payload, options=options
        ).json()

    def get_expected_exceptions(self):
        res = super().get_expected_exceptions()
        res.append(MissingGithubError)
        return res

    @api.model
    def postprocess_response_error(self, response):
        """Override to raise exception instead of logging."""
        if response.status_code == 404:
            Exc = MissingGithubError
        else:
            Exc = ValidationError
        _raise_endpoint_error(response, Exc)

    def _call_github_http_method(self, verb, path, payload=None, options=None):
        options = self._prepare_request_options(path, payload=payload, options=options)
        _logger.debug(
            'Request -> Method: %s. Path: %s. Payload:\n%s',
            verb,
            path,
            payload,
        )
        response = self.call_http_method(verb, options=options)
        _logger.debug(
            'Response -> Method: %s. Path: %s. Status: %s. Response:\n%s',
            verb,
            path,
            response.status_code,
            response.text,
        )
        return response

    def _prepare_request_options(self, path, payload=None, options=None):
        if options is None:
            options = {}
        options.setdefault('kwargs', {})
        if payload is not None:
            options['kwargs']['json'] = payload
        headers = options['kwargs'].setdefault('headers', {})
        headers.update(**EXTRA_HEADERS)
        if 'path_item' not in options:
            options['path_item'] = PathItem(path_expression=path)
        return options
