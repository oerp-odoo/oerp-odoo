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
    records, fname, predicate=None, case_insensitive=False, raise_exc=True
):
    """Check if existing record field value is unique.

    Args:
        records: records to check field value uniqueness for.
        fname: field name to check
        predicate: function to check iterate record, whether uniqueness
            check is needed. Expects single record as an argument.
        case_insensitive: whether to use case insensitive search. This
            option has no effect if field is not char or text type.
        raise_exc: whether to raise exception if field is not unique.

    """

    def get_domain(rec):
        domain = get_main_domain(rec)
        if hasattr(records, 'company_id'):
            domain.append(('company_id', '=', rec.company_id.id))
        return domain

    def get_main_domain(rec):
        return [('id', '!=', rec.id), (fname, operator, rec[fname])]

    if predicate is None:
        predicate = _predicate_dummy
    operator = '='
    ctx = {'active_test': False}
    # We can only use case insensitive check for text fields.
    if records._fields[fname].type in ('char', 'text'):
        operator = OP_EQ_MAP[case_insensitive]
        if case_insensitive:
            # unaccent function is incompatible with ilike search,
            # as it makes it very inefficient search. And odoo forces
            # it when using ilike. Though such uniqueness search
            # should not need to use unaccent at all (if there would
            # be some non ASCII symbols involved in unaccent
            # it could even incorrectly match)
            ctx['force_disable_unaccent'] = True
    domain_func = get_domain
    flabel = records._fields[fname]._description_string(records.env)
    for rec in records.filtered(fname):
        if not predicate(rec):
            continue
        if records.with_context(**ctx).sudo().search(domain_func(rec), limit=1):
            msg = records.env._(
                "%(flabel)s '%(fvalue)s' must be unique!",
                flabel=flabel,
                fvalue=rec[fname],
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


def _predicate_dummy(record):
    return True
