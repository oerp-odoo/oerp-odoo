from werkzeug.exceptions import HTTPException

orig_get_description = HTTPException.get_description


def get_description(self, environ=None):
    if getattr(self, '_description_without_html', None):
        return self.description
    return orig_get_description(self, environ=environ)


HTTPException.get_description = get_description
