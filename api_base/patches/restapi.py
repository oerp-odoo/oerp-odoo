from pydantic import validate_model

from odoo.addons.base_rest_pydantic.restapi import PydanticModel

orig_to_response = PydanticModel.to_response


def to_response(self, service, result):
    """Override to implement extra config options.

    - ignore_response_validation: to return response without any
        validation.
    - exclude_none: to be able to generate response without None values
    """
    # CUSTOM CODE START
    cfg = result.__config__
    kw = {}
    if hasattr(cfg, 'exclude_none') and cfg.exclude_none:
        kw['exclude_none'] = True
    json_dict = result.dict(**kw)
    # There seems to be a bug that when response is expected to contain attribute
    # that is list of other pydantic models, it fails to validate. It even crashes
    # raising an exception properly.. So for now we patch this to ignore
    # validation when custom config parameter is passed.
    if hasattr(cfg, 'ignore_response_validation') and cfg.ignore_response_validation:
        return json_dict
    # CUSTOM CODE END
    # do we really need to validate the instance????
    to_validate = (
        json_dict if not result.__config__.orm_mode else result.dict(by_alias=True)
    )
    *_, validation_error = validate_model(self._model_cls, to_validate)
    if validation_error:
        raise SystemError(_("Invalid Response %s") % validation_error)
    return json_dict
    # cfg = result.__config__
    # if hasattr(cfg, 'ignore_response_validation') and cfg.ignore_response_validation:
    #     return result.dict()
    # return orig_to_response(self, service, result)


PydanticModel.to_response = to_response
