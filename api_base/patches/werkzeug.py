import inspect

from werkzeug.exceptions import HTTPException

orig_get_description = HTTPException.get_description

orig_signature = inspect.signature(orig_get_description)

if 'scope' in orig_signature.parameters:

    def get_description(self, environ=None, scope=None):
        if getattr(self, '_description_without_html', None):
            return self.description
        return orig_get_description(self, environ=environ, scope=scope)

else:

    def get_description(self, environ=None):
        if getattr(self, '_description_without_html', None):
            return self.description
        return orig_get_description(self, environ=environ)


HTTPException.get_description = get_description
