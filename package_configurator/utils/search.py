def search_record_by_context_key(model, ctx_key, fname='code', limit=1):
    val = model.env.context.get(ctx_key)
    if not val:
        return model
    return model.search([(fname, '=', val)], limit=limit)


def search_default_component_kind(model):
    return search_record_by_context_key(
        model.env['package.component.kind'], 'package_component_kind_code'
    )
