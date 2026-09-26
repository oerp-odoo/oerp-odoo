import logging

from psycopg2 import OperationalError

from odoo.exceptions import ValidationError
from odoo.fields import Domain
from odoo.service.model import PG_CONCURRENCY_ERRORS_TO_RETRY
from odoo.tools.safe_eval import safe_eval

from ..const import OP_EQ_MAP

_logger = logging.getLogger(__name__)


# NOTE. We must have first argument named exactly `self` for translations
# to work properly.
def validate_domain_field(self, field_name, model_name, eval_context=None):
    """Check if field content is correct domain."""

    def check_domain(rec, domain):
        try:
            domain = safe_eval(domain, eval_context)
            Domain.normalize_domain(domain)
            self.env[model_name].search(domain, limit=1)
        except (ValueError, SyntaxError, KeyError, AssertionError) as e:
            raise ValidationError(
                self.env_(
                    "%(description)s for record '%(name)s' is incorrect. Error:\n%(e)s",
                    description=self._fields[field_name]._description_string(self.env),
                    name=rec.display_name,
                    e=e,
                )
            )

    eval_context = eval_context or {}
    for rec in self:
        domain = rec[field_name]
        if domain:
            check_domain(rec, domain)


def check_field_unique(
    record,
    fname,
    predicate=None,
    extra_domain: Domain | None = None,
    case_insensitive=False,
    raise_exc=True,
):
    """Check if existing record field value is unique.

    Args:
        record: record to check field value uniqueness for.
        fname: field name to check
        predicate: function to check record, whether uniqueness
            check is needed. Expects single record as an argument.
        extra_domain: extra domain to filter uniqueness check further.
        case_insensitive: whether to use case insensitive search. This
            option has no effect if field is not char or text type.
        raise_exc: whether to raise exception if field is not unique.

    """

    def get_domain():
        domain = get_main_domain()
        if hasattr(record, 'company_id'):
            domain &= Domain('company_id', '=', record.company_id.id)
        if extra_domain is None:
            return domain
        return domain & extra_domain

    def get_main_domain():
        return Domain('id', '!=', record.id) & Domain(fname, operator, record[fname])

    record.ensure_one()
    if not record.filtered(fname):
        return True
    if predicate is not None and not predicate(record):
        return True
    operator = '='
    ctx = {'active_test': False}
    # We can only use case insensitive check for text fields.
    if record._fields[fname].type in ('char', 'text'):
        operator = OP_EQ_MAP[case_insensitive]
        if case_insensitive:
            # unaccent function is incompatible with ilike search,
            # as it makes it very inefficient search. And odoo forces
            # it when using ilike. Though such uniqueness search
            # should not need to use unaccent at all (if there would
            # be some non ASCII symbols involved in unaccent
            # it could even incorrectly match)
            ctx['force_disable_unaccent'] = True
    flabel = record._fields[fname]._description_string(record.env)
    if record.with_context(**ctx).sudo().search(get_domain(), limit=1):
        msg = record.env._(
            "%(flabel)s '%(fvalue)s' must be unique!",
            flabel=flabel,
            fvalue=record[fname],
        )
        if raise_exc:
            raise ValidationError(msg)
        _logger.info(msg)
        return False
    return True


def is_retryable_concurrency_error(e):
    return (
        isinstance(e, OperationalError) and e.pgcode in PG_CONCURRENCY_ERRORS_TO_RETRY
    )
