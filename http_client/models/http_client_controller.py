import logging
import traceback
from urllib.parse import urljoin, urlparse

import mergedeep
import requests

from odoo import _, api, models
from odoo.exceptions import ValidationError

from ..exceptions import AuthDataError

_logger = logging.getLogger(__name__)


def get_endpoint(base_url, uri_expression, args=None):
    """Return endpoint using base URL and URI pattern.

    Args:
        base_url (str): base URL for endpoint.
        uri_expression (str): URI expression that is appended to
            base URL to form endpoint.
        args (tuple): extra arguments to render variables in
            endpoint if there are any (default: {None}).

    If base_url has path, it will be appended to uri_expression as if it
    was its prefix.

    Returns:
        str: generated endpoint.

    """
    # Parse to keep base_url without path or params.
    url_obj = urlparse(base_url)
    base_url = (
        f'{url_obj.scheme}://{url_obj.netloc}' if url_obj.scheme else url_obj.netloc
    )
    url_path = url_obj.path
    if url_path:
        # We keep path without ending `/` if there is one, to make sure
        # that we can always combine it with `uri_expression`
        url_path = url_path[:-1] if url_path.endswith('/') else url_path
        uri_expression = f'{url_path}{uri_expression}'
    endpoint = urljoin(base_url, uri_expression)
    if args:
        return endpoint % args
    return endpoint


def _extract_response_body(response):
    # TODO: implement body types: content, body, raw, exc.
    content_type = response.headers.get('content-type', '')
    if 'application/json' in content_type:
        return response.json()
    return response.text


def _prepare_endpoint_error_data(response):
    msg_pattern = "Endpoint '%s' call failed. Method: %s, Error Code: %s, Response: %s"
    return (
        msg_pattern,
        (
            response.url,
            response.request.method,
            response.status_code,
            response.text,
        ),
    )


def _log_endpoint_error(response):
    msg_pattern, error_data = _prepare_endpoint_error_data(response)
    _logger.error(msg_pattern, *error_data)


def _raise_endpoint_error(response, exc):
    msg_pattern, args = _prepare_endpoint_error_data(response)
    error_msg = msg_pattern % args
    raise exc(error_msg)


class HttpClientController(models.AbstractModel):
    """Base model as a client side controller with remote system.

    This model must be inherited when implementing specific controller.
    """

    _name = 'http.client.controller'
    _description = "HTTP Client Controller"
    _auth_model = None

    @api.model
    def _get_auth_data(self, company_id, auth=None):
        if auth:
            return auth.get_data()
        if self._auth_model:
            auth = self.env[self._auth_model].get_auth(company_id)
            if auth:
                return auth.get_data()

    @api.model
    def is_controller_enabled(self):
        """Return True if controller is enabled, False otherwise.

        Override to implement enabler logic.
        """
        return True

    @api.model
    def postprocess_response_error(self, response):
        """Log error using response object.

        Can be overridden to implement different error handling logic.
        """
        _log_endpoint_error(response)

    @api.model
    def postprocess_response_ok(self, response):
        """Override to add extra logic when response is successful."""

    @api.model
    def _check_response(self, response):
        """Check if returned response is successful."""
        if not response.ok:
            self.postprocess_response_error(response)
            return False
        self.postprocess_response_ok(response)
        return True

    def _validate_endpoint_with_uri_item(self, endpoint, uri_item):
        if not (bool(endpoint) ^ bool(uri_item)):
            raise ValidationError(
                _(
                    "Programming error: endpoint and uri_item must satisfy"
                    + " XOR condition."
                )
            )

    @api.model
    def _merge_kwargs_with_auth(self, kwargs, auth_data):
        if auth_data and auth_data['auth']:
            mergedeep.merge(kwargs, auth_data['auth'])

    @api.model
    def call_http_method(self, method_name, options=None):
        """Call specified REST method.

        Args:
            method_name: HTTP verb to use (e.g GET).
            options (dict): options for REST method calls:
                endpoint (str): endpoint path to use in REST call
                    (default: {None}).
                uri_item (tuple): two pair tuple, where first item is
                    uri_expression and second, optional tuple of
                    endpoint arguments. endpoint and uri_item have
                    exclusive OR condition (default: {None}).
                company_id (int): company ID to use in finding related
                    auth object if there is any (default: {None}).
                auth (http.client.auth): auth object to be used
                    explicitly. If specified, auth is not searched and
                    company_id is ignored.
                kwargs (dict): extra keyword arguments for call, like
                    payload, auth headers etc. (default: {None}).

        Returns:
            response obj

        Raises:
            ValidationError

        """

        def get_endpoint_from_uri_item(uri_item, auth_data):
            uri_expression, endpoint_args = uri_item
            try:
                url = auth_data['url']
            except TypeError:
                raise AuthDataError(
                    _(
                        "No Authentication object found to get base URL. "
                        + "Check Authentication objects configuration."
                    )
                )
            return get_endpoint(url, uri_expression, args=endpoint_args)

        if not options:
            options = {}
        endpoint, uri_item = options.get('endpoint'), options.get('uri_item')
        self._validate_endpoint_with_uri_item(endpoint, uri_item)
        auth_data = self._get_auth_data(
            options.get('company_id', False), auth=options.get('auth')
        )
        kwargs = options.get('kwargs', {})
        self._merge_kwargs_with_auth(kwargs, auth_data)
        if uri_item:
            endpoint = get_endpoint_from_uri_item(uri_item, auth_data)
        method = getattr(requests, method_name)
        try:
            response = method(endpoint, **kwargs)
            self._check_response(response)
            return response
        # We raise on unexpected exceptions.
        except Exception:
            raise ValidationError(traceback.format_exc())
