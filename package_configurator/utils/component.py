def get_comps(comps, *comp_types, keep_empty=True):
    def filter_comps(comps, ctype):
        return comps.filtered(lambda r: r.component_type_id.code == ctype)

    res = []
    for ctype in comp_types:
        comp = filter_comps(comps, ctype)
        if not comp and not keep_empty:
            continue
        # Adding even if there is no comp found, to make it more
        # flexible.
        res.append(comp)
    return res
