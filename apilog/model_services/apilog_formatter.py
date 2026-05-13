import json

from requests.structures import CaseInsensitiveDict

from odoo import models

from ..const import JSON_INDENT
from ..utils import detect_content_type


class ApilogFormatter(models.AbstractModel):
    _name = 'apilog.formatter'
    _description = "API Log Formatter"

    def format(self, data: str, headers: str):
        if not data:
            return data
        headers = self._parse_headers(headers)
        format_type = detect_content_type(headers)
        if format_type is None:
            return data
        formatter = getattr(self, f'format_{format_type}')
        try:
            return formatter(data)
        # We can't assume that provided data is always correct!
        except Exception:
            return data

    def format_json(self, data: str):
        return json.dumps(json.loads(data), indent=JSON_INDENT)

    def _parse_headers(self, headers: str):
        return CaseInsensitiveDict(json.loads(headers))
