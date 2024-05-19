from odoo.exceptions import ValidationError

from ..models.res_config_settings import CFG_PARAM_PRODUCT_CODE_UNIQUE
from . import common


class TestProductCodeUniqueness(common.TestProductCommon):
    """Tests to check product code uniqueness."""

    def test_01_code_unique(self):
        """Test assigning same code when company is the same."""
        # Should raise, because both code and company are the same.
        with self.assertRaises(ValidationError):
            self.product_2.default_code = 'E-COM07'

    def test_02_code_unique(self):
        """Test assigning same code for template when company is the same."""
        # Should raise, because both code and company are the same.
        with self.assertRaises(ValidationError):
            self.product_2.product_tmpl_id.default_code = 'E-COM07'

    def test_03_code_unique(self):
        """Test with the same code but company is not set in one product."""
        # Should raise, because codes are the same and one product has no
        # company set.
        with self.assertRaises(ValidationError):
            self.product_2.write({'default_code': 'E-COM07', 'company_id': False})

    def test_04_code_unique(self):
        """Test the same code but company is not set in product template."""
        # Should raise, because codes are the same and one product template
        # has no company set.
        with self.assertRaises(ValidationError):
            self.product_2.product_tmpl_id.write(
                {'default_code': 'E-COM07', 'company_id': False}
            )

    def test_05_code_unique(self):
        """Test case when one product w/o company already has the same code."""
        # Should raise, because codes are the same and one product has no
        # company set.
        self.product_1.company_id = False
        with self.assertRaises(ValidationError):
            self.product_2.default_code = 'E-COM07'

    def test_06_code_unique(self):
        """Test when product template w/o company already has the same code."""
        # Should raise, because codes are the same and one product template has
        # no company set.
        self.product_1.product_tmpl_id.company_id = False
        with self.assertRaises(ValidationError):
            self.product_2.product_tmpl_id.default_code = 'E-COM07'

    def test_07_code_unique(self):
        """Test product same code, but different company.

        Case: product_comp_rule disabled.
        """
        self.product_comp_rule.active = False
        with self.assertRaises(ValidationError):
            self.product_2.write(
                {
                    'default_code': 'E-COM07',
                    'company_id': self.demo_company_id,
                }
            )

    def test_08_code_unique(self):
        """Test product same code, but different company.

        Also test when setting same company back.
        Case: product_comp_rule enabled.
        """
        try:
            # Should not raise ValidationError, because products have
            # different companies.
            self.product_2.write(
                {
                    'default_code': 'E-COM07',
                    'company_id': self.demo_company_id,
                }
            )
        except ValidationError:
            self.fail("Should not have raised ValidationError.")
        with self.assertRaises(ValidationError):
            self.product_2.company_id = self.main_company_id
        # Check when changing company from product.template.
        with self.assertRaises(ValidationError):
            self.product_2.product_tmpl_id.company_id = self.main_company_id

    def test_09_code_unique(self):
        """Test assigning unique code to product."""
        try:
            # Should not raise ValidationError, because code is unique.
            self.product_2.default_code = 'some_unique_code_1234'
        except ValidationError:
            self.fail("Should not have raised ValidationError.")

    def test_10_code_unique(self):
        """Test assigning unique code to product template."""
        try:
            # Should not raise ValidationError, because code is unique.
            self.product_2.product_tmpl_id.default_code = 'some_unique_code_12'
        except ValidationError:
            self.fail("Should not have raised ValidationError.")

    def test_11_code_unique(self):
        """Test case-insensitive uniqueness with the same code ending."""
        self.IrConfigParameter.set_param(
            CFG_PARAM_PRODUCT_CODE_UNIQUE, 'enabled_insensitive'
        )
        try:
            # Should not raise ValidationError, because code is unique.
            self.product_2.default_code = 'EE-COM07'
        except ValidationError:
            self.fail("Should not have raised ValidationError.")

    def test_12_code_unique(self):
        """Test case-insensitive uniqueness with the same code (lower case)."""
        # Should raise, because both code and company are the same.
        self.IrConfigParameter.set_param(
            CFG_PARAM_PRODUCT_CODE_UNIQUE, 'enabled_insensitive'
        )
        with self.assertRaises(ValidationError):
            self.product_2.default_code = 'e-com07'

    def test_13_code_unique(self):
        """Test case-sensitive uniqueness with the same code in lower case."""
        try:
            # Should not raise ValidationError, because code is unique
            self.product_2.default_code = 'e-com07'
        except ValidationError:
            self.fail("Should not have raised ValidationError.")

    def test_14_code_unique(self):
        """Test with the same code when uniqueness is disabled."""
        self.IrConfigParameter.set_param(CFG_PARAM_PRODUCT_CODE_UNIQUE, 'disabled')
        try:
            # Should not raise ValidationError, because product code's
            # uniqueness check is disabled.
            self.product_2.default_code = 'E-COM07'
        except ValidationError:
            self.fail("Should not have raised ValidationError.")

    def test_15_code_unique(self):
        """Test with the same code when uniqueness parameter is not set."""
        self.IrConfigParameter.set_param(CFG_PARAM_PRODUCT_CODE_UNIQUE, False)
        try:
            # Should not raise ValidationError, because product code's
            # uniqueness check is disabled.
            self.product_2.default_code = 'E-COM07'
        except ValidationError:
            self.fail("Should not have raised ValidationError.")

    def test_16_code_unique(self):
        """Test code uniqueness with inactive product."""
        # Should raise, because both code and company are the same.
        self.IrConfigParameter.set_param(
            CFG_PARAM_PRODUCT_CODE_UNIQUE, 'enabled_insensitive'
        )
        self.product_1.active = False
        with self.assertRaises(ValidationError):
            self.product_2.default_code = 'e-com07'

    def test_17_code_unique(self):
        """Test code uniqueness when original has no default_code."""
        self.IrConfigParameter.set_param(
            CFG_PARAM_PRODUCT_CODE_UNIQUE, 'enabled_insensitive'
        )
        self.product_1.default_code = False
        try:
            self.product_1.copy()
        except ValidationError:
            self.fail("Should not raise, because code is not set.")
