from odoo.tools import float_round

DIGITS = 2


def calc_engraving_time(stamp_cfg, digits=DIGITS):
    time_ = _calc_engraving_time(stamp_cfg)
    if stamp_cfg.design_id.is_embossed:
        time_ = _calc_engraving_time_with_embossed_design(stamp_cfg, time_)
    return float_round(time_, precision_digits=digits)


def _calc_engraving_time(stamp_cfg, design=None):
    design = design or stamp_cfg.design_id
    speed = design.engraving_speed
    coefficient = stamp_cfg.difficulty_id.coefficient
    return stamp_cfg.area / 100 * speed / 60 * coefficient


def _calc_engraving_time_with_embossed_design(stamp_cfg, time_):
    time_with_emb = time_ * stamp_cfg.embossed_design_perc / 100
    design = stamp_cfg.design_id.design_base_embossed_id
    return time_with_emb + _calc_engraving_time(stamp_cfg, design=design)
