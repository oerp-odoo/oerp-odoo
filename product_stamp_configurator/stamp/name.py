from odoo import _

from .code import get_design_code_with_pfx

THICKNESS_UOM = 'mm'


def get_word(self, key):
    # NOTE. First argument must be named `self` explicitly and it must
    # be odoo record (recordset) for translations to work.
    labels = {
        'molding_prefix': _('Molding service'),
        'counter_die': _('Counter-Die'),
        'pieces': _('pcs'),
        'spare': _('Spare'),
    }
    return labels[key]


def generate_die_name(stamp_cfg):
    return _generate_die_name(
        stamp_cfg,
        stamp_cfg.material_id,
        stamp_cfg.die_id.name,
        stamp_cfg.quantity_spare_dies,
        with_design_code_pfx=False,
        with_design_name=True,
    )


def generate_counter_die_name(stamp_cfg):
    return _generate_die_name(
        stamp_cfg,
        stamp_cfg.material_counter_id,
        get_word(stamp_cfg, 'counter_die'),
        stamp_cfg.quantity_counter_spare_dies,
        with_design_code_pfx=True,
        with_design_name=False,
    )


def generate_mold_name(stamp_cfg):
    design_code = get_design_code_with_pfx(stamp_cfg)
    molding_prefix = get_word(
        stamp_cfg,
        'molding_prefix',
    )
    return f'{molding_prefix} {design_code}{stamp_cfg.sequence}'


def _generate_die_name(
    stamp_cfg,
    material,
    die_name,
    quantity,
    with_design_code_pfx=False,
    with_design_name=False,
):
    material_label = material.label_id.name
    design = stamp_cfg.design_id
    if with_design_code_pfx:
        design_code = get_design_code_with_pfx(stamp_cfg)
    else:
        design_code = stamp_cfg.design_id.code
    thickness = material.thickness
    code = f'{material_label} {die_name}'
    if with_design_name:
        code = f'{code}, {design.name}'
    code = f'{code}, {design_code}{stamp_cfg.sequence}, {thickness:g} {THICKNESS_UOM}'
    if quantity:
        spare_word = get_word(stamp_cfg, 'spare')
        piece_word = get_word(stamp_cfg, 'pieces')
        code = f'{code}+ {spare_word} {quantity} {piece_word}'
    return code
