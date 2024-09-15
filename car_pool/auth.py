import hashlib
import hmac
import secrets

SALT_LENGTH = 16
HASH_ITERATIONS = 100000
HASH_ALGORITHM = "sha256"
HASH_LENGTH = 32


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(SALT_LENGTH)

    hashed_password = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,  # Hash algorithm
        password.encode("utf-8"),  # Convert the password to bytes
        salt,  # Salt
        HASH_ITERATIONS,  # Number of iterations
        HASH_LENGTH,  # Length of the hash
    )
    return f"{salt.hex()}:{hashed_password.hex()}"


def verify_password(stored_password: str, password_attempt: str) -> bool:
    salt_hex, stored_hash_hex = stored_password.split(":")

    salt = bytes.fromhex(salt_hex)
    stored_hash = bytes.fromhex(stored_hash_hex)

    attempt_hash = hashlib.pbkdf2_hmac(
        HASH_ALGORITHM,
        password_attempt.encode("utf-8"),
        salt,
        HASH_ITERATIONS,
        HASH_LENGTH,
    )

    return hmac.compare_digest(stored_hash, attempt_hash)
