import re

# TODO: implement configurable options.
DEFAULT_DESIGN_SEQ_CODE_RE = r"(({})\d+)"
DEFAULT_INSERT_DIE_CODE = 'i'


def parse_design_seq_code(code: str, design_codes: tuple) -> str:
    """Extract design type code with its sequence."""
    pattern = DEFAULT_DESIGN_SEQ_CODE_RE.format('|'.join(design_codes))
    m = re.search(pattern, code)
    if not m:
        return ""
    return m.group()


def is_insert_die_code(code: str) -> bool:
    return DEFAULT_INSERT_DIE_CODE == code


def is_insert_die_in_code(code: str, design_codes: tuple) -> bool:
    """Check if die code is next to design code in specified code."""
    seq_design_code = parse_design_seq_code(code, design_codes)
    if not seq_design_code:
        return False
    # Remove matched sequence as we only need matched design code.
    design_code = re.sub(r'\d', '', seq_design_code)
    i_design_code = f'{DEFAULT_INSERT_DIE_CODE}{design_code}'
    return parse_design_seq_code(code, (i_design_code,))
