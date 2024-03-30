from psycopg2 import IntegrityError

from odoo.exceptions import ValidationError
from odoo.tools.misc import mute_logger

from odoo.addons.server_environment import serv_config

from . import common


class TestAuthBasicConfig(common.TestAuthBasicCommon):
    """Test cases for basic.auth configuration."""

    def test_01_basic_auth_name_unique(self):
        """Check if name uniqueness works."""
        with self.assertRaises(IntegrityError), mute_logger('odoo.sql_db'):
            self.AuthBasic.create(
                {
                    'name': self.auth_basic_1.name,
                    'user_id': self.user_admin.id,
                    'username': 'demo2',
                    'password': 'demo2_123',
                }
            )

    def test_02_credentials(self):
        """Check if credentials encode username, password correctly."""
        self.assertEqual(
            self.auth_basic_1._credentials,
            # demo:demo_123
            'ZGVtbzpkZW1vXzEyMw==',
        )
        self.auth_basic_1.username = 'chipmunk'
        self.assertEqual(
            self.auth_basic_1._credentials,
            # chipmunk:demo_123
            'Y2hpcG11bms6ZGVtb18xMjM=',
        )

    def test_03_credentials(self):
        """Check if server env overwrites existing credentials."""
        section = 'auth_basic.%s' % self.auth_basic_1.name
        serv_config.add_section(section)
        serv_config.set(section, 'username', 'test')
        serv_config.set(section, 'password', 'test_123')
        self.assertEqual(
            # test:test_123
            self.AuthBasic._retrieve_auth_basic('dGVzdDp0ZXN0XzEyMw=='),
            self.auth_basic_1,
        )
        with self.assertRaises(ValidationError):
            # Old credentials demo:demo_123
            self.AuthBasic._retrieve_auth_basic('ZGVtbzpkZW1vXzEyMw==')

    def test_04_retrieve_auth_basic_id(self):
        """Retrieve auth_basic_id using credentials.

        Case 1: retrieve auth_basic_id and cache it.
        Case 2: retrieve same auth_basic_id using cache.
        Case 3: try to retrieve with no longer valid credentials
            (cache cleared by writing).
        Case 4: use new creds to get ID and cache it.
        Case 5: try to retrieve ID with no longer valid credentials (
            cache cleared by unlink).
        """
        # Case 1.
        credentials = self.auth_basic_1._credentials
        auth_basic_1_id = self.auth_basic_1.id
        auth_basic_id = self.AuthBasic._retrieve_auth_basic_id(credentials)
        self.assertEqual(auth_basic_1_id, auth_basic_id)
        # Case 2.
        auth_basic_id = self.AuthBasic._retrieve_auth_basic_id(credentials)
        self.assertEqual(auth_basic_1_id, auth_basic_id)
        # Case 3
        self.auth_basic_1.password = 'abcdefg'
        with self.assertRaises(ValidationError):
            self.AuthBasic._retrieve_auth_basic_id(credentials)
        # Case 4.
        credentials = self.auth_basic_1._credentials
        auth_basic_id = self.AuthBasic._retrieve_auth_basic_id(credentials)
        self.assertEqual(auth_basic_1_id, auth_basic_id)
        # Case 5.
        self.auth_basic_1.unlink()
        with self.assertRaises(ValidationError):
            self.AuthBasic._retrieve_auth_basic_id(credentials)
