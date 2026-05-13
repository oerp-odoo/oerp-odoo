from odoo.tests.common import TransactionCase

from ..tools.crypto import generate_signature, sign_sha256

SECRET_1 = b"secret123"
DATA_1 = b"data123"


class TestCrypto(TransactionCase):
    def test_01_generate_signature_raw(self):
        # WHEN
        signature = generate_signature(SECRET_1, DATA_1)
        # THEN
        self.assertEqual(
            signature,
            b"\x1bC\xb7\xecxY:\xe8\xa0\x7f\x84\x89\x18^e\xbdG5]\x10 \xa5\xc5Z"
            + b"\x9a\x0e\xd9\xb7\x02\xb2\\\x89",
        )

    def test_02_generate_signature_b64(self):
        # WHEN
        signature = generate_signature(SECRET_1, DATA_1, to_base64=True)
        # THEN
        self.assertEqual(signature, b"G0O37HhZOuigf4SJGF5lvUc1XRAgpcVamg7ZtwKyXIk=")

    def test_03_generate_signature_hex(self):
        # WHEN
        signature = generate_signature(SECRET_1, DATA_1, to_hex=True)
        # THEN
        self.assertEqual(
            signature,
            b"1b43b7ec78593ae8a07f8489185e65bd47355d1020a5c55a9a0ed9b702b25c89",
        )

    def test_04_sign_sha_256(self):
        # GIVEN
        timestamp = 1768985813
        # WHEN
        sig = sign_sha256(SECRET_1, DATA_1, timestamp)
        # THEN
        self.assertEqual(
            sig,
            "sha256=2a86a0a82fe696f316d85f365599608031d46166ccad8ecd192d9ec7ea9324ba",
        )
