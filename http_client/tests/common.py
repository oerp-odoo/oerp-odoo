import base64
import json

from requests.structures import CaseInsensitiveDict

from odoo.tests.common import TransactionCase


def encode_jwt_token(p1=None, p2=None, p3=None, no_padding=True):
    def encode_part(part):
        p = base64.b64encode(json.dumps(part).encode()).decode()
        # In real case scenario tokens have no padding, so we can
        # simulate that.
        if no_padding:
            p = p.replace('=', '')
        return p

    if p1 is None:
        p1 = {}
    if p2 is None:
        p2 = {}
    if p3 is None:
        p3 = {}
    p1, p2, p3 = encode_part(p1), encode_part(p2), encode_part(p3)
    r = f'{p1}.{p2}.{p3}'
    return r


# MODELS_PATH = 'odoo.models'
CONTENT_TYPE_APPLICATION_JSON = CaseInsensitiveDict(
    {'Content-Type': 'application/json; charset=utf-8'}
)
DUMMY_URL = 'http://127.0.0.1'
DUMMY_PATH = '/my_path'
DUMMY_ENDPOINT = f"{DUMMY_URL}{DUMMY_PATH}"


class TestHttpClientCommon(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.company_main = cls.env.ref('base.main_company')
        cls.HttpClient = cls.env['http.client']
        cls.HttpClientRetry = cls.env['http.client.retry']
        cls.HttpClientAuth = cls.env['http.client.auth']
        cls.HttpClientEncoder = cls.env['http.client.encoder']
        cls.HttpClientProfile = cls.env['http.client.profile']
        cls.HttpClientTransport = cls.env['http.client.transport']
