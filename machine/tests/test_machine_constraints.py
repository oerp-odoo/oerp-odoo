from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tools import mute_logger

from . import common


class TestMachineConstraints(common.TestMachineCommon):
    """Class to machine module constraints."""

    def test_01_check_ip(self):
        """Set IP to check its validity.

        Case 1: invalid IP.
        Case 2: valid IP.
        """
        # Case 1.
        with self.assertRaises(ValidationError):
            self.machine_instance_wood.ip = '123456'
        # Case 2.
        try:
            self.machine_instance_wood.ip = '1.1.1.1'
        except ValidationError:
            self.fail("Valid IP must pass.")

    def test_02_check_domain(self):
        """Set domain to check its validity.

        Case 1: invalid domain.
        Case 2: valid domain.
        """
        # Case 1.
        with self.assertRaises(ValidationError):
            self.machine_instance_wood.domain = 'http://focusate.eu'
        # Case 2.
        try:
            self.machine_instance_wood.domain = 'focusate.eu'
        except ValidationError:
            self.fail("Valid domain must pass.")

    @mute_logger('odoo.sql_db')
    def test_03_machine_name_unique(self):
        """Try to set same name globally."""
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.machine_instance_deco.name = self.machine_instance_wood.name

    @mute_logger('odoo.sql_db')
    def test_04_machine_name_unique(self):
        """Try to set same name when same company is set."""
        (self.machine_instance_wood | self.machine_instance_deco).mapped(
            'partner_id'
        ).write({'company_id': self.company_main.id})
        with self.assertRaises(IntegrityError):
            with self.cr.savepoint():
                self.machine_instance_deco.name = self.machine_instance_wood.name

    def test_05_machine_name_unique(self):
        """Set same name when companies are different."""
        self.machine_instance_deco.partner_id.company_id = self.company_main.id
        try:
            self.machine_instance_deco.name = self.machine_instance_wood.name
            with self.cr.savepoint():
                self.machine_instance_deco.name = self.machine_instance_wood.name
        except IntegrityError:
            self.fail("Companies are different, so same name must be allowed.")
