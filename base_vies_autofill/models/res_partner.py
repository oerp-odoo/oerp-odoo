import logging

from stdnum.exceptions import InvalidComponent

from odoo import api, models

_logger = logging.getLogger(__name__)

EMPTY_VAL = '---'


def _is_not_empty_vies_val(val):
    return val and val != EMPTY_VAL


class ResPartner(models.Model):
    """Extend to fill partner data from VIES."""

    _inherit = 'res.partner'

    def _is_vies_autofill_enabled(self):
        if self._context.get('company_id'):
            company = self.env['res.company'].browse(self._context['company_id'])
        else:
            company = self.env.company
        return company.vat_check_vies and company.vies_autofill

    @api.model
    def retrieve_vies_data(self, vat):
        """Call VIES service and validate VAT with extra data."""
        if not self._is_vies_autofill_enabled():
            return {}
        try:
            res = self._check_vies(vat)
            # Using same handling as in `vies_vat_check` method. Though
            # we can't reuse it, because it cuts vies results to only
            # whether VAT is valid, but we need all the data that it
            # returns.
        except InvalidComponent:
            return {}
        except Exception:
            _logger.exception("Failed VIES VAT check.")
            return {}
        data = {'valid': res['valid'], 'vals': {}}
        vals = data['vals']
        if _is_not_empty_vies_val(res['name']):
            vals['name'] = res['name']
        if _is_not_empty_vies_val(res['address']):
            vals['street'] = res['address'].replace('\n', ', ')
        if _is_not_empty_vies_val(res['countryCode']):
            country = self.env['res.country'].search(
                [('code', '=', res['countryCode'].upper())]
            )
            if country:
                vals['country_id'] = country.id
        return data

    @api.onchange('vat')
    def _onchange_vat(self):
        if self.vat and self.is_company:
            res = self.retrieve_vies_data(self.vat)
            if res:
                self.update(
                    # Update only if its not set already.
                    {k: v for k, v in res['vals'].items() if not self[k]}
                )
