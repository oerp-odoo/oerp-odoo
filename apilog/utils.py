import base64
import inspect
import io
import os
import zipfile
from contextlib import contextmanager

from requests.structures import CaseInsensitiveDict
from werkzeug.wrappers import Response as WerkzeugResponse

from odoo import SUPERUSER_ID, api
from odoo.modules.registry import Registry

from odoo.addons.odootil.tools.crypto import make_hash

from .const import MAX_CALL_STACK, Format, ZipCompressLevel


@contextmanager
def get_env(db: str, readonly=False, context=None):
    if context is None:
        context = {}
    with Registry(db).cursor(readonly=readonly) as cr:
        env = api.Environment(cr, SUPERUSER_ID, context)
        yield env
        cr.commit()  # pylint: disable=invalid-commit


def to_werkzeug_response(result):
    if isinstance(result, WerkzeugResponse):
        response = result
    # Assuming result is then HTTPException
    else:
        response = result.get_response()
    if hasattr(result, 'traceback'):
        response.traceback = result.traceback
    return response


def get_data_safely(obj, as_text=True):
    """Attempt to retrieve data from request or response object safely.

    If any error occurs, we ignore it as this is intended only for
    logging, so we can't block it!
    Data might not be available all the time, like when streaming bytes
    or incompatible encoding is used.
    """
    try:
        return obj.get_data(as_text=as_text) or None
    except Exception:
        return None


def get_simple_call_stack(limit=MAX_CALL_STACK) -> list[tuple]:
    """Return call stack info, which namespace, method/function was called.

    It will return up to specified limit upstream calls.

    For example if limit is 10, it will show 10 calls that happened
    before this was called (excluding this call itself).
    """
    stack = inspect.stack()[1 : limit + 1]  # Skip this function itself
    calls = []
    for frame_info in stack:
        func_name = frame_info.function
        namespace = _get_call_class_name(frame_info)
        if namespace is None:
            namespace = _get_call_filename(frame_info)
        calls.append((namespace, func_name))
    return calls


def detect_content_type(headers: CaseInsensitiveDict):
    if headers.get('Content-Type') == 'application/json':
        return Format.JSON
    return None


def form_filename(
    base_name: str, headers: CaseInsensitiveDict, default_extension='txt'
):
    extension = default_extension
    content_type = detect_content_type(headers)
    if content_type:
        # Assuming extension matches content type!
        extension = content_type
    return f'{base_name}.{extension}'


def zip_data(
    filename: str, data: bytes, compress_level=ZipCompressLevel.DEFAULT
) -> io.BytesIO:
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(
        zip_buffer,
        mode="w",
        compression=zipfile.ZIP_DEFLATED,
        compresslevel=compress_level,
    ) as zf:
        zf.writestr(filename, data)
    return zip_buffer


def zip_with_base64(
    filename: str, data: bytes, compress_level=ZipCompressLevel.DEFAULT
) -> bytes:
    compressed_data = zip_data(filename, data, compress_level=compress_level).getvalue()
    return base64.b64encode(compressed_data)


@contextmanager
def unzip_data(data: bytes):
    with zipfile.ZipFile(io.BytesIO(data), 'r') as zf:
        yield zf


def unzip_from_base64(data: bytes):
    return unzip_data(base64.b64decode(data))


def prepare_open_related_logs_action(record):
    action = record.env['ir.actions.act_window']._for_xml_id('apilog.apilog_log_action')
    action.update(
        {
            'view_mode': 'tree',
            'domain': [
                ('res_model', '=', record._name),
                ('res_id', '=', record.id),
            ],
        }
    )
    return action


def sanitize_headers(headers: dict):
    headers = CaseInsensitiveDict(headers)
    if headers.get('Authorization'):
        # We don't want to show auth data directly, so we hash it.
        headers['Authorization'] = make_hash(headers['Authorization'])
    # To be JSON friendly!
    return dict(headers)


def _get_call_class_name(frame_info):
    def get_first_arg_class(frame):
        try:
            first_arg_name = frame.f_code.co_varnames[0]
        except IndexError:
            return None
        first_arg = frame.f_locals[first_arg_name]
        if inspect.isclass(first_arg):
            return first_arg
        return first_arg.__class__

    frame = frame_info.frame
    code = frame.f_code
    func_name = code.co_name
    cls = get_first_arg_class(frame)
    if cls is None:
        return None
    try:
        method = getattr(cls, func_name)
    except AttributeError:
        return None
    if method.__code__ == code:
        return cls.__name__
    return None


def _get_call_filename(frame_info):
    return os.path.splitext(os.path.basename(frame_info.filename))[0]
