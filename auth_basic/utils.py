import hashlib


def make_hash(value: str):
    return hashlib.sha256(value.encode()).hexdigest()
