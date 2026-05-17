"""Files handling and their data manipulation helpers."""

import importlib
import os
import pathlib
import re

import jinja2

from odoo.modules.module import get_module_path
from odoo.tools import convert
from odoo.tools.misc import file_open

# Excluding all these characters, should make it valid for windows files
# like excel.
INVALID_FILENAME_ALPHABET = r'\t\\#&%\${}<>\*\?/ !\'":@\+`\|=\[\]'


def convert_file_realpath(cfg):
    """Import file data into odoo using file's real path.

    This is reimplementation of convert_file, except it accepts real
    path and not odoo module's relative path, and path here is
    required (original argument is pathname) and filename argument is
    not used, because it is taken from path.
    """
    cr, module, path = cfg['cr'], cfg['module'], cfg['path']
    idref = cfg.get('idref')
    mode = cfg.get('mode', 'update')
    noupdate = cfg.get('noupdate', False)
    filename = os.path.basename(path)
    ext = os.path.splitext(filename)[1].lower()
    with open(path) as f:
        if ext == '.csv':
            convert.convert_csv_import(
                cr, module, path, f.read(), idref, mode, noupdate
            )
        elif ext == '.sql':
            convert.convert_sql_import(cr, f)
        elif ext == '.xml':
            convert.convert_xml_import(
                cr, module, f, idref, mode, noupdate, report=cfg.get('report')
            )
        elif ext == '.js':
            pass  # .js files are valid but ignored here.
        else:
            raise ValueError("Can't load unknown file type %s.", filename)


# Render helpers.


def render_file_template(path, variables, encoding='utf-8'):
    """Render data from file template using specified variables.

    Jinja2 engine is used to render template, so its syntax is expected.

    Args:
        path (str): path to data template file. If path is relative
            path, it will be treated as relative path from odoo module.
        variables (dict): data to be used when rendering template.
        encoding (str): encoding to encode data before returning it. If
            set to False, will not encode it. (default: {'utf-8'})

    Returns:
        rendered data.
        str or bytes

    """

    def render_template(template):
        data = template.render(**variables)
        if encoding:
            return data.encode(encoding)
        return data

    # We assume that relative path is path from odoo module, so we
    # use file_open that is appropriate for such path.
    fopen = open if os.path.isabs(path) else file_open
    with fopen(path) as f:
        template = jinja2.Template(f.read())
        return render_template(template)


def parse_filename(
    filename: str,
    space_replacer=None,
    fallback_symbol='',
    ascii_only=False,
    invalid_chars=INVALID_FILENAME_ALPHABET,
):
    """Parse provided filename removing invalid characters.

    Args:
        filename: file name to parse
        space_replacer: whether to explicitly replace space with other
            symbol.
        fallback_symbol: symbol to use in place of invalid characters.
        ascii_only: whether to keep only ASCII characters.
        invalid_chars: invalid characters alphabet

    Returns:
        parsed filename

    """
    if space_replacer is not None:
        filename = filename.replace(' ', space_replacer)
    if ascii_only:
        filename = filename.encode('ascii', 'ignore').decode()
    parts = re.compile(rf'[{invalid_chars}]+').split(filename)
    return fallback_symbol.join(parts)


def load_py_module(name: str, module: str, path: pathlib.Path):
    """Load python module from odoo module path.

    Args:
        name (str): name space to give to loaded python module.
        module (str): odoo module name to load py module from.
        path (pathlib.Path): relative path from odoo module.

    """
    path_module = get_module_path(module)
    spec = importlib.util.spec_from_file_location(
        name=name,
        location=pathlib.Path(path_module) / path,
    )
    py_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(py_module)
    return py_module


def load_py_attribute(ref: str):
    """Load py attribute using dotted path reference."""
    module_path, attr = ref.rsplit(".", 1)
    module = importlib.import_module(module_path)
    return getattr(module, attr)
