import base64
import hashlib

from cryptography.hazmat.primitives import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes


def _evp_bytes_to_key(passphrase: bytes, salt: bytes, key_len: int = 32, iv_len: int = 16):
    # OpenSSL's EVP_BytesToKey (MD5, 1 iteration) - the key derivation CryptoJS uses
    # when AES is given a plain string secret.
    derived = b""
    block = b""
    while len(derived) < key_len + iv_len:
        block = hashlib.md5(block + passphrase + salt).digest()
        derived += block
    return derived[:key_len], derived[key_len:key_len + iv_len]


def decrypt(encrypted):
    raw = base64.b64decode(encrypted)
    salt = raw[8:16]  # layout: "Salted__" + 8 byte salt + ciphertext
    ciphertext = raw[16:]

    key, iv = _evp_bytes_to_key("=l!RoGMxgMko=88Z4#5*?Vl.@".encode("utf-8"), salt)

    decryptor = Cipher(algorithms.AES(key), modes.CBC(iv)).decryptor()
    padded = decryptor.update(ciphertext) + decryptor.finalize()

    unpadder = padding.PKCS7(128).unpadder()
    decrypted = unpadder.update(padded) + unpadder.finalize()

    return decrypted.decode("utf-8")
