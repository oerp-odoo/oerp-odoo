from odoo.exceptions import ValidationError

from ..pydantic_models.partner import PartnerResponse
from . import common


class TestPmOrm(common.TestApiBaseCommon):
    def test_01_orm_response_missing_required_field(self):
        # GIVEN
        partner = self.ResPartner.create({'type': 'other'})
        # WHEN, THEN
        with self.assertRaisesRegex(
            ValidationError,
            r"Data mismatch\. Response for .+ can't be generated\. Mandatory field "
            + r"name is not set in backend model res\.partner\.",
        ):
            PartnerResponse.from_orm(partner)
