import operator
import re
from urllib.parse import urljoin, urlparse

from footil.formatting import strip_space
from requests.models import PreparedRequest

from .value_objects import PathItem

OP_RANGE_MAP = {
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
}


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


def get_next_link(response, key: str) -> str | None:
    try:
        return response.links[key]['url']
    except KeyError:
        return None


# TODO: this could go to footil.
# TODO: add support for float.
def match_number(number: int, expr: str) -> bool:
    """Match number by a given number or range conditions.

    Args:
        number: number that is either matched via range expr or not.
        expr: single numbers, range or ranges expression. For
            example: '100,200,!251,>=250,<300' would match numbers 100, 200,
            greater or equal to 250 (except 251) and lower than 300.
            Note exact numbers in expr are combined with not equal and range
            expr using OR operator, where not equal and ranges themselves are
            combined with AND operator.

    """
    inclusions, exclussions = _form_match_number_conditions(expr)
    # If we have inclusion match, then it ignores exclusion!
    for n in inclusions:
        if number == n:
            return True
    if not exclussions:
        return False
    for op, n in exclussions:
        if not op(number, n):
            return False
    return True


def _form_match_number_conditions(expr: str):
    inclusions = []
    exclusions = []
    # We ignore all spaces.
    for part in strip_space(expr).split(','):
        # First try to match exact number.
        try:
            inclusions.append(int(part))
        except ValueError:
            msg = (
                f"Invalid expression: {expr}. Expression can only contain numbers,"
                + " not equal numbers and range expressions separated by commas. "
                + "For example: 100,!=201,>=200,<300"
            )
            # Now we assume that its ether not equal or range expr.
            m = re.search(r'\d+', part)
            if not m:
                raise ValueError(msg)
            n = m.group()
            op_str = part.replace(n, '')
            try:
                op = OP_RANGE_MAP[op_str]
            except KeyError:
                raise ValueError(msg)
            exclusions.append((op, int(n)))
    return (inclusions, exclusions)
