from unittest.mock import patch

from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase
from odoo.tools import mute_logger

from ..tools.decor import mute_validation_by_ctx


def check_dummy(self):
    raise ValidationError("Exception!")  # pylint: disable=C8107


class TestMuteValidationByCtx(TransactionCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.ResPartner = cls.env['res.partner']

    @mute_logger('odoo.addons.odootil.tools.decor')
    def test_01_mute_validation_by_generic_ctx(self):
        PartnerType = type(self.ResPartner)
        with patch.object(PartnerType, 'check_dummy', check_dummy, create=True):
            ResPartner = self.ResPartner.with_context(validation_mute=True)
            decorated = mute_validation_by_ctx(PartnerType.check_dummy)
            decorated_method = decorated.__get__(ResPartner, PartnerType)
        try:
            decorated_method()
        except ValidationError as e:
            self.fail(
                "Must be able to ignore validation with validation_mute "
                + f"ctx! Error: {e}"
            )

    @mute_logger('odoo.addons.odootil.tools.decor')
    def test_02_mute_validation_by_generic_ctx(self):
        PartnerType = type(self.ResPartner)
        with patch.object(PartnerType, 'check_dummy', check_dummy, create=True):
            ResPartner = self.ResPartner.with_context(check_dummy_mute=True)
            decorated = mute_validation_by_ctx(PartnerType.check_dummy)
            decorated_method = decorated.__get__(ResPartner, PartnerType)
        try:
            decorated_method()
        except ValidationError as e:
            self.fail(
                "Must be able to ignore validation with check_dummy_mute "
                + f"ctx! Error: {e}"
            )

    def test_03_mute_validation_by_wrong_ctx(self):
        PartnerType = type(self.ResPartner)
        with patch.object(PartnerType, 'check_dummy', check_dummy, create=True):
            ResPartner = self.ResPartner.with_context(check_some_other_mute=True)
            decorated = mute_validation_by_ctx(PartnerType.check_dummy)
            decorated_method = decorated.__get__(ResPartner, PartnerType)
        with self.assertRaisesRegex(ValidationError, r"Exception!"):
            decorated_method()
