COUNTER_DIE_PFX = 'P'


def generate_die_code(stamp_cfg):
    extra_code = stamp_cfg.material_id.code
    if stamp_cfg.finishing_id:
        extra_code = f'{extra_code}{stamp_cfg.finishing_id.code}'
    return _generate_code(stamp_cfg, extra_code)


def generate_mold_code(stamp_cfg):
    return _generate_code(stamp_cfg, _get_counter_die_sequence(stamp_cfg))


def generate_counter_die_code(stamp_cfg):
    cdie_seq = _get_counter_die_sequence(stamp_cfg)
    extra_code = f'{cdie_seq}{stamp_cfg.material_counter_id.code}'
    return _generate_code(stamp_cfg, extra_code)


def get_design_code_with_pfx(stamp_cfg):
    c = stamp_cfg
    die_code = stamp_cfg.die_id.code
    return f'{die_code or ""}{c.design_id.code}'


def _generate_code(stamp_cfg, extra_code):
    code = _get_base_code(stamp_cfg)
    code = f'{code}{extra_code}'
    return _get_code_with_ref(code, stamp_cfg.ref)


def _get_base_code(stamp_cfg):
    seq = stamp_cfg.sequence
    return f'{stamp_cfg.origin}{get_design_code_with_pfx(stamp_cfg)}{seq}'


def _get_code_with_ref(code, ref):
    return f'{code} / {ref}'


# Used by both counter die and mold.
def _get_counter_die_sequence(stamp_cfg):
    return f'P{stamp_cfg.sequence_counter_die}'
