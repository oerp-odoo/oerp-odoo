from apispec import BasePlugin


class BasicSecurityPlugin(BasePlugin):
    def __init__(self, service):
        super().__init__()
        self._service = service

    def init_spec(self, spec):
        super().init_spec(spec)
        self.spec = spec
        self.openapi_version = spec.openapi_version
        api_key_scheme = {'type': 'apiKey', 'in': 'header', 'name': 'AUTHORIZATION'}
        spec.components.security_scheme('basic', api_key_scheme)

    def operation_helper(self, path=None, operations=None, **kwargs):
        routing = kwargs.get('routing')
        if not routing:
            super().operation_helper(path, operations, **kwargs)
        if not operations:
            return
        default_auth = self.spec._params.get('default_auth')
        auth = routing.get('auth', default_auth)
        if auth == 'basic' or (auth == 'public_or_default' and default_auth == 'basic'):
            for _method, params in operations.items():
                security = params.setdefault('security', [])
                security.append({'basic': []})
