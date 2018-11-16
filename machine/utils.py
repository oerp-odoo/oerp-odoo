from string import Formatter
from operator import attrgetter


def generate_name(pattern, obj, strip_falsy=True):
    """Generate name by pattern, using attributes specified by it.

    Object is used to get required attributes values. If object does not
    have truthy value for attribute, it can be stripped using keyword
    argument strip_falsy.

    Args:
        pattern (str): pattern to generate name by. e.g.
            'test {a.b} / {c}'
        obj (object): object to retrieve attributes from.
        strip_falsy (bool): whether to strip away falsy attribute values
            or not. If stripped away, then leading string
            is also stripped away for next attribute to not look like
            '/ attr_value'. It instead just looks like 'attr_value'
            (default: {True}).

    Returns:
        Generated name using pattern and obj attributes.
        str

    """
    def get_prev_attr_val():
        attr_vals_len = len(attrs_vals)
        if attr_vals_len > 1:
            return attrs_vals[attr_vals_len-2]

    def get_leading_str(leading_str):
        prev_attr_val = get_prev_attr_val()
        # None means, current item is first and there is no previous
        # one.
        if prev_attr_val is None:
            return leading_str
        # We have falsy value (on prev attribute) and we need to strip
        # it away, so we use empty string.
        if not prev_attr_val and strip_falsy:
            return ''
        return leading_str

    name = ''
    # To track previous attribute value.
    attrs_vals = []
    for item in Formatter().parse(pattern):
        # Get attribute value from attr key. We use attrgetter from
        # operator module to be able to access n-depth attributes. In
        # Other words access attribute of objects that are related with
        # another object.
        f = attrgetter(item[1])  # item[1] is attribute key.
        attr_val = f(obj)
        attrs_vals.append(attr_val)
        # item[0] holds original leading string.
        leading_str = get_leading_str(item[0])
        if attr_val or not strip_falsy:
            name += leading_str + str(attr_val)
    return name


def generate_name_get(pattern, records):
    """Wrap generate_name and reuse for name_get methods case."""
    return [(rec.id, generate_name(pattern, rec)) for rec in records]
