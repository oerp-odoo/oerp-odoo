from odoo.exceptions import ValidationError

from odoo.addons.base_rest.controllers.main import _PseudoCollection
from odoo.addons.component.core import WorkContext


def get_component_service(
    env, collection_name: str, usage: str, model_name='rest.service.registration'
):
    """Get component service from specific collection/usage/model."""
    collection = _PseudoCollection(collection_name, env)
    services_env = WorkContext(model_name=model_name, collection=collection)
    return services_env.component(usage=usage)


def get_record_id_by_domain(Model, domain, limit=None, raise_not_found=True):
    record = Model.search(domain, limit=limit)
    if not record:
        if raise_not_found:
            description = Model._description
            raise ValidationError(f"No {description} found using domain {domain}")
        return None
    if len(record) > 1:
        raise ValidationError(
            f"Found more than one record ({Model._name}) using domain {domain}"
        )
    return record.id


def get_record_id_by_name(Model, name, limit=None, raise_not_found=True):
    return get_record_id_by_domain(
        Model,
        [('name', '=', name)],
        limit=limit,
        raise_not_found=raise_not_found,
    )


def get_partner_id_by_vat(env, vat: str):
    # Forcing limit, to make search faster. Though we must be sure
    # VAT uniqueness is guaranteed.
    company_id = env.user.company_id.id
    return get_record_id_by_domain(
        env['res.partner'],
        domain=[('vat', '=', vat), ('company_id', 'in', (False, company_id))],
        limit=1,
    )


def validate_record_exists(record, msg=None):
    if not msg:
        msg = f"{record._description} with ID {record.id} does not exist"
    if not record.exists() or hasattr(record, 'active') and not record.active:
        raise ValidationError(msg)
    # From outside, if it tries to access record outside that user companies,
    # it means it can't.
    if hasattr(record, 'company_id'):
        if record.company_id and record.company_id not in record.env.companies:
            raise ValidationError(msg)
    return True


def get_record_by_xmlid(env, xmlid, msg):
    try:
        record = env.ref(xmlid)
    except ValueError:
        raise ValidationError(msg)
    validate_record_exists(record, msg=msg)
    return record


def get_country_id(env, country_code):
    country_id = env['res.country'].search([('code', '=ilike', country_code)]).id
    if not country_id:
        raise ValidationError(f"Country not found with code {country_code}")
    return country_id
