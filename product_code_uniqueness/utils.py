from odoo import _
from odoo.osv import expression

# TODO: move these to more general module.


def build_default_code(obj, default):
    """Set default_code when duplicating data.

    Args:
        obj: product.product or product.template record
        default: dictionary to update for copy data.

    """
    default_code = obj.default_code
    # Leave original default_code (False) if it is not set.
    if default_code:
        if default is None:
            default = {}
        default.setdefault('default_code', default_code + _(" (copy)"))
    return default


def search_multicompany(
    model_obj, domain, offset=0, limit=None, order=None, options=None
):
    """Find multi-company friendly records by domain.

    Intended to be used for fields where value uniqueness must be
    preserved.

    Uniqueness checked globally if objects are shared across
    multiple companies, otherwise current object company is used.

    Args:
        model_obj: odoo Model to search on.
        domain: base domain for search. Should not include
            multi-company leaf.
        offset (int): number of results to ignore (default: {0})
        limit (int): maximum number of records to return (default:
            {None})
        order (str): sort string (default {None})
        options (dict): extra options to modify search. Dict can
                have such keys. (default: {None}):
            multi_comp_rule_xml_id (str): multi company ir.rule
                XMLID that is used to identify if multi-company is
                used for that object. Optional (default: {None}).
            company_id (int): company ID that is used for multi
                company domain. If multi_company_rule_xml_id is not
                used and company_id is specified, it will be force
                used in domain. Optional (default: {False}).
            active_test (bool): whether to include inactive records.
                False value means include (default: {False}).

    Returns:
        recordset

    """
    return __prepare_search_multicompany_method(
        model_obj, domain, offset=offset, limit=limit, order=order, options=options
    )()


def search_multicompany_count(model_obj, domain, options=None):
    """Find multi-company friendly records count by domain.

    Intended to be used for fields where value uniqueness must be
    preserved.

    Uniqueness checked globally if objects are shared across
    multiple companies, otherwise current object company is used.

    Args:
        model_obj: odoo Model to search on.
        domain: base domain for search. Should not include
            multi-company leaf.
            {None})
        options (dict): extra options to modify search. Dict can
                have such keys. (default: {None}):
            multi_comp_rule_xml_id (str): multi company ir.rule
                XMLID that is used to identify if multi-company is
                used for that object. Optional (default: {None}).
            company_id (int): company ID that is used for multi
                company domain. If multi_company_rule_xml_id is not
                used and company_id is specified, it will be force
                used in domain. Optional (default: {False}).
            active_test (bool): whether to include inactive records.
                False value means include (default: {False}).

    Returns:
        recordset

    """
    return __prepare_search_multicompany_method(model_obj, domain, options=options)(
        count=True
    )


def __prepare_search_multicompany_method(
    model_obj, domain, offset=0, limit=None, order=None, options=None
):
    def is_multi_comp_used(multi_comp_rule_xml_id, company_id):
        # Multi company is used, if there is explicit rule to
        # enable/disable it or if company_id was passed as argument.
        # Multi company rule takes priority.
        if multi_comp_rule_xml_id:
            # Rule that defines if multi-company rule is enabled (
            # shared globally or per company)
            return (
                model_obj.sudo().env.ref(multi_comp_rule_xml_id).active
                # Can filter per company, only if company is passed,
                # otherwise would filter for partners that have no
                # company set only.
                and company_id
            )
        return bool(company_id)

    def get_company_domain(multi_comp_rule_xml_id, company_id):
        if is_multi_comp_used(multi_comp_rule_xml_id, company_id):
            return [('company_id', 'in', [company_id, False])]
        return []

    def to_multicompany_domain(domain):
        company_domain = get_company_domain(
            options.get('multi_comp_rule_xml_id'),
            options.get('company_id', False),
        )
        return expression.AND([domain, company_domain])

    def _search_multicompany_method(count=False):
        if count:
            return model_obj.with_context(active_test=active_test).search_count(
                domain, limit=limit
            )
        return model_obj.with_context(active_test=active_test).search(
            domain, offset=offset, limit=limit, order=order
        )

    if not options:
        options = {}
    domain = to_multicompany_domain(domain)
    active_test = options.get('active_test', False)
    return _search_multicompany_method
