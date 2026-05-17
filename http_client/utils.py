import base64
import datetime
import json
import operator
import re
from urllib.parse import urlparse

import validators
from footil.formatting import strip_space
from requests.models import PreparedRequest

from odoo.exceptions import ValidationError
from odoo.tools.urls import urljoin

from .const import B64_PADDING
from .value_objects.request import RelativePath

OP_RANGE_MAP = {
    '!=': operator.ne,
    '>': operator.gt,
    '>=': operator.ge,
    '<': operator.lt,
    '<=': operator.le,
}


def check_url(env, url):
    """Check URL validity.

    Args:
        url (str): url to check

    Returns:
        None

    Raises:
        ValidationError if not valid

    """
    # Using '' as default, to make sure False value is not passed,
    # which cant be validated by validators.url.
    if not validators.url(url or ''):
        raise ValidationError(env._("'%s' is not valid URL.", url))
    return True


def build_url(base_url: str, relative_path: RelativePath):
    """Return URL using base URL and RelativePath.

    Args:
        base_url: base URL for endpoint.
        relative_path: path data to combine with base_url.

    If base_url has path, it will be appended to relative_path as if it
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
    pattern = relative_path.pattern
    if url_path:
        # We keep path without ending `/` if there is one, to make sure
        # that we can always combine it with `pattern`
        url_path = url_path[:-1] if url_path.endswith('/') else url_path
        pattern = f'{url_path}{relative_path.pattern}'
    endpoint = urljoin(base_url, pattern)
    if relative_path.args:
        endpoint = endpoint.format(*relative_path.args)
    if relative_path.params:
        req = PreparedRequest()
        req.prepare_url(endpoint, relative_path.params)
        endpoint = req.url
    return endpoint


def get_next_link(response, key: str) -> str | None:
    try:
        return response.links[key]['url']
    except KeyError:
        return None


def is_jwt_token_expired(token, delta=0):
    """Check if token expiration date has passed.

    Args:
        token (str): encoded JWT token.
        delta (int): number of seconds to move expiration. Negative
            value can be used to make sure we don't end up with expired
            token after it was checked and expired few seconds later.

    Returns:
        True if token has expired, False otherwise.

    """
    # We only care about second part as it should hold information
    # when token expires.
    # Compare only up to a second as token usually holds only that info.
    now_stamp = int(datetime.datetime.now().timestamp())
    p2 = f"{token.split('.')[1]}{B64_PADDING}"
    token_timestamp = json.loads(base64.b64decode(p2))['exp']
    return token_timestamp + delta <= now_stamp


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
