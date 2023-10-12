from base64 import urlsafe_b64decode, urlsafe_b64encode
from Crypto.Cipher import AES
from Crypto.Cipher import _mode_cbc

_IV = b'\x00' * 16

class NameCryptor:
    def __init__(self, key: bytes):
        super().__init__()
        self.key = key

    def get_cipher(self) -> _mode_cbc.CbcMode:
        return AES.new(self.key, AES.MODE_CBC, iv=_IV) # type: ignore

    def encrypt(self, name: str) -> str:
        cipher = self.get_cipher()
        return '/'.join([self.encrypt_one(part, cipher) for part in name.split('/')])

    def encrypt_one(self, name: str, cipher: _mode_cbc.CbcMode) -> str:
        if not name:
            return ''

        name_bytes = name.encode('utf-8')
        name_bytes += b'\x00' * (16 - (len(name_bytes) % 16))
        ciphertext = cipher.encrypt(name_bytes)

        return urlsafe_b64encode(ciphertext).decode('utf-8')

    def decrypt(self, name: str) -> str:
        cipher = self.get_cipher()
        return '/'.join([self.decrypt_one(part, cipher) for part in name.split('/')])

    def decrypt_one(self, name: str, cipher: _mode_cbc.CbcMode) -> str:
        if not name:
            return ''

        ciphertext = cipher.decrypt(urlsafe_b64decode(name))

        return ciphertext.decode('utf-8').rstrip('\x00')
