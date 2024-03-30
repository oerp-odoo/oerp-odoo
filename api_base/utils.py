from odoo.exceptions import MissingError, ValidationError


def get_record_id_by_domain(Model, domain, limit=None, raise_not_found=True):
    record = Model.search(domain, limit=limit)
    if not record:
        if raise_not_found:
            description = Model._description
            raise MissingError(f"No {description} found using domain {domain}")
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


def validate_record_exists(record, msg=None):
    if not msg:
        msg = f"{record._description} with ID {record.id} does not exist"
    if not record.exists() or hasattr(record, 'active') and not record.active:
        raise MissingError(msg)
    return True


def get_country_id(env, country_code):
    country_id = env['res.country'].search([('code', '=ilike', country_code)]).id
    if not country_id:
        raise MissingError(f"Country not found with code {country_code}")
    return country_id
