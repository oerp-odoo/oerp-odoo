"""Data formatting helpers."""

import unicodedata

import odoo.tools


def email_formatter(keep_name=True):
    """Return function that will format email tuple.

    Tuple must consist of email name and email itself.
    """

    def format_email_only(email_item):
        return odoo.tools.formataddr((False, email_item[1]))

    def format_email_full(email_item):
        name, email = email_item
        # We don't want to have formatted email as
        # `"a@a.com" <a@a.com>`.
        if name == email:
            return format_email_only(email_item)
        return odoo.tools.formataddr((name, email))

    if keep_name:
        return format_email_full
    # Return plain email
    return format_email_only


def unaccent(s: str) -> str:
    """Replace unicode letters with ASCII equivalent."""
    return unicodedata.normalize('NFD', s).encode('ascii', 'ignore').decode()
