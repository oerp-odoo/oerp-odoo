import functools
import operator


def get_nested(data: dict, keys: list, default=None) -> any:
    """Retrieve value from nested dict safely."""
    # Adding safe guard so it would not be possible to accidentally
    # pass non dict input and silently get default value.
    _ensure_dict(data)
    try:
        return functools.reduce(operator.getitem, keys, data)
    # Including TypeError to also be forgiving when we encounter unexpected
    # type while iterating, it means we should also use default.
    except (KeyError, TypeError):
        return default


def pop_nested(data: dict, keys: list) -> any:
    """Pop keys in nested dict safely."""
    _ensure_dict(data)
    if len(keys) == 1:
        return data.pop(keys[0], None)
    key = keys[-1]
    inner_dct = get_nested(data, keys[:-1])
    if not isinstance(inner_dct, dict):
        return None
    return inner_dct.pop(key, None)


def _ensure_dict(data: dict):
    if not isinstance(data, dict):
        raise TypeError(
            f"Expected a Mapping (e.g. dict) as input, got {type(data).__name__}"
        )
    return True
