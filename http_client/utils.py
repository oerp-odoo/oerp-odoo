from urllib.parse import urljoin, urlparse

from requests.models import PreparedRequest

from .value_objects import PathItem


def get_endpoint(base_url: str, path_item: PathItem):
    """Return endpoint using base URL and PathItem.

    Args:
        base_url: base URL for endpoint.
        path_item: path data to combine with base_url.

    If base_url has path, it will be appended to path_item as if it
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
    path_expression = path_item.path_expression
    if url_path:
        # We keep path without ending `/` if there is one, to make sure
        # that we can always combine it with `path_expression`
        url_path = url_path[:-1] if url_path.endswith('/') else url_path
        path_expression = f'{url_path}{path_item.path_expression}'
    endpoint = urljoin(base_url, path_expression)
    if path_item.args:
        endpoint = endpoint.format(*path_item.args)
    if path_item.params:
        req = PreparedRequest()
        req.prepare_url(endpoint, path_item.params)
        endpoint = req.url
    return endpoint
