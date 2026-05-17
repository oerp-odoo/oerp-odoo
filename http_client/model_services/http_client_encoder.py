import json
from urllib.parse import urlencode

from odoo import models

from .. import const


class HttpClientEncoder(models.AbstractModel):
    _name = 'http.client.encoder'
    _description = "HTTP Client Encoder"

    def encode(self, data: any, format_type: str) -> tuple:
        try:
            method_name = f'_encode_{format_type}'
            method = getattr(self, method_name)
            return method(data)
        except AttributeError:
            raise ValueError(f"{format_type} format encoding is not supported!")

    def _encode_raw(self, data):
        return (data, None)

    def _encode_json(self, data):
        encoded_data = json.dumps(
            data, separators=(",", ":"), ensure_ascii=False, sort_keys=True
        ).encode(encoding='utf-8')
        return (encoded_data, const.MIMETYPE_JSON)

    def _encode_form(self, data):
        return (urlencode(data, doseq=True).encode('utf-8'), const.MIMETYPE_FORM)
