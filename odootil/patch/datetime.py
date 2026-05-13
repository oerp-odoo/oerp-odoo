from odoo import fields


@staticmethod
def context_timestamp_iso(record, dt=None):
    """Get datetime in ISO format.

    Args:
        dt (str, date, datetime): date/datetime string or object
            (default: {None}).

    Returns:
        datetime in ISO format, e.g. '2018-01-22T08:19:54+01:00'.
        str

    """
    if not dt:
        dt = fields.Datetime.now()
    return fields.Datetime.context_timestamp(
        record, fields.Datetime.to_datetime(dt)
    ).isoformat()


fields.Datetime.context_timestamp_iso = context_timestamp_iso
