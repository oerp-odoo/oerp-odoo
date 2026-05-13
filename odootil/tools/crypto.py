import base64
import hashlib
import hmac


def generate_signature(
    secret: bytes,
    data: bytes,
    to_hex: bool = False,
    to_base64: bool = False,
    digestmethod=hashlib.sha256,
) -> bytes:
    res = hmac.new(secret, data, digestmethod)
    sig = res.hexdigest().encode() if to_hex else res.digest()
    if to_base64:
        sig = base64.b64encode(sig)
    return sig


def make_hash(value: str):
    return hashlib.sha256(value.encode()).hexdigest()


def sign_sha256(secret: bytes, data: bytes, timestamp: int):
    """Sign SHA256 HEX signature with sha256= prefix."""
    d = f'{str(timestamp)}:{data.decode()}'.encode()
    sig = generate_signature(secret, d, to_hex=True).decode()
    return f'sha256={sig}'
