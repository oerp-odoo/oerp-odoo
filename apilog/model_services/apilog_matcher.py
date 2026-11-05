import re

from odoo import _, models
from odoo.exceptions import ValidationError
from odoo.tools.safe_eval import safe_eval, safe_whitelist

from odoo.addons.odootil.value_objects.http import HttpVerb

from ..value_objects import ApilogMatcherInput

# 20.0 safe_eval warns on functions that are not whitelisted.
safe_whitelist.add_function('re.match')


class ApilogMatcher(models.AbstractModel):
    _name = 'apilog.matcher'
    _description = "API Log Matcher"

    def match(self, expression: str, inp: ApilogMatcherInput):
        return bool(safe_eval(expression, self._prepare_match_context(inp)))

    def check_match(self, expression):
        """Validate if expression is syntactically correct."""
        try:
            self.match(
                expression,
                # Using dummy data to just pass some input.
                inp=ApilogMatcherInput(
                    endpoint='http://localhost',
                    verb=HttpVerb.GET,
                    status_code=200,
                ),
            )
        except Exception as e:
            raise ValidationError(_("Incorrect expression syntax. Error: %s", e))
        return True

    def _prepare_match_context(self, inp: ApilogMatcherInput):
        return {'inp': inp, 're_match': re.match}
