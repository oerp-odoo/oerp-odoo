import requests

from odoo import models
from odoo.exceptions import ValidationError

from ..utils import build_url
from ..value_objects.request import RequestInput
from ..value_objects.session import HttpSessionSettingsRetry


class HttpClientTransport(models.AbstractModel):
    _name = 'http.client.transport'
    _description = "HTTP Client Transport"

    def request(self, inp: RequestInput):
        self._validate_input(inp)
        with requests.Session() as session:
            self._configure_session(session, inp)
            return session.request(**self._prepare_request_params(inp))

    def _validate_input(self, inp: RequestInput):
        if not inp.profile.active:
            raise ValidationError(
                self.env._("HTTP Client Profile (%s) is inactive!", inp.profile.name)
            )

    def _prepare_request_params(self, inp: RequestInput) -> dict:
        profile = inp.profile
        params = {
            'method': inp.method,
            'url': inp.url or build_url(profile.base_url, inp.relative_path),
            'headers': inp.headers,
        }
        if inp.data:
            data, content_type = self.env['http.client.encoder'].encode(
                inp.data, inp.data_format_type
            )
            params['data'] = data
            if content_type:
                params['headers']['Content-Type'] = content_type
        auth = profile.auth_id
        params['headers'].update(auth.authorize())
        return params

    def _configure_session(self, session: requests.Session, inp: RequestInput):
        retry = inp.profile.retry_id
        if not retry:
            return
        retry_settings = HttpSessionSettingsRetry.from_record(retry)
        adapter = requests.adapters.HTTPAdapter(max_retries=retry_settings.retry)
        for mnt_pfx in retry_settings.mount_prefixes:
            session.mount(mnt_pfx, adapter)
