import base64
import secrets
import string

class DataEncryption:
    def __init__(self, key: str = "ATS_SECURE_KEY_2025"):
        self.key = key
        self.caesar_shift = self._generate_caesar_shift(key)
        self.xor_key = self._generate_xor_key(key)

    def _generate_caesar_shift(self, key: str) -> int:
        shift = sum(ord(c) for c in key) % 26
        return shift if shift > 0 else 13

    def _generate_xor_key(self, key: str) -> bytes:
        key_bytes = key.encode("utf-8")
        return (key_bytes * (16 // len(key_bytes) + 1))[:16]

    def _caesar_encrypt(self, text: str, shift: int) -> str:
        result = ""
        for char in text:
            if char.isalpha():
                ascii_offset = 65 if char.isupper() else 97
                shifted = (ord(char) - ascii_offset + shift) % 26
                result += chr(shifted + ascii_offset)
            else:
                result += char
        return result

    def _caesar_decrypt(self, text: str, shift: int) -> str:
        return self._caesar_encrypt(text, -shift)

    def _xor_encrypt_decrypt(self, data: bytes, key: bytes) -> bytes:
        key_len = len(key)
        return bytes([b ^ key[i % key_len] for i, b in enumerate(data)])

    def _custom_substitution(self, text: str, encrypt: bool = True) -> str:
        normal = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"
        cipher = "ZYXWVUTSRQPONMLKJIHGFEDCBAzyxwvutsrqponmlkjihgfedcba9876543210"
        trans_table = str.maketrans(normal, cipher) if encrypt else str.maketrans(cipher, normal)
        return text.translate(trans_table)

    def encrypt(self, plaintext: str) -> str:
        if not plaintext:
            return ""
        step1 = self._custom_substitution(plaintext, encrypt=True)
        step2 = self._caesar_encrypt(step1, self.caesar_shift)
        step3_bytes = step2.encode('utf-8')
        step3_encrypted = self._xor_encrypt_decrypt(step3_bytes, self.xor_key)
        return base64.b64encode(step3_encrypted).decode('utf-8')

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        step1_bytes = base64.b64decode(ciphertext.encode('utf-8'))
        step2_bytes = self._xor_encrypt_decrypt(step1_bytes, self.xor_key)
        step2 = step2_bytes.decode('utf-8')
        step3 = self._caesar_decrypt(step2, self.caesar_shift)
        return self._custom_substitution(step3, encrypt=False)

    def encrypt_dict(self, data_dict: dict, fields_to_encrypt: list) -> dict:
        encrypted_dict = data_dict.copy()
        for field in fields_to_encrypt:
            if field in encrypted_dict and encrypted_dict[field] is not None:
                encrypted_dict[field] = self.encrypt(str(encrypted_dict[field]))
        return encrypted_dict

    def decrypt_dict(self, data_dict: dict, fields_to_decrypt: list) -> dict:
        decrypted_dict = data_dict.copy()
        for field in fields_to_decrypt:
            if field in decrypted_dict and decrypted_dict[field] is not None:
                decrypted_dict[field] = self.decrypt(str(decrypted_dict[field]))
        return decrypted_dict

    def verify_encryption(self, original: str, encrypted: str) -> bool:
        return original == self.decrypt(encrypted)

    def change_key(self, new_key: str) -> None:
        self.key = new_key
        self.caesar_shift = self._generate_caesar_shift(new_key)
        self.xor_key = self._generate_xor_key(new_key)

    def get_encryption_info(self) -> dict:
        return {
            "caesar_shift": self.caesar_shift,
            "xor_key_length": len(self.xor_key),
            "encryption_layers": [
                "Custom Substitution Cipher",
                "Caesar Cipher",
                "XOR Cipher",
                "Base64 Encoding"
            ]
        }

def generate_secure_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def encrypt_sensitive_cv_data(cv_data: dict) -> dict:
    encryption = DataEncryption()
    sensitive_fields = [
        'name', 'email', 'phone', 'address',
        'personal_info', 'contact_details'
    ]
    encrypted_data = cv_data.copy()
    for field in sensitive_fields:
        if field in encrypted_data and encrypted_data[field]:
            if isinstance(encrypted_data[field], str):
                encrypted_data[field] = encryption.encrypt(encrypted_data[field])
            elif isinstance(encrypted_data[field], list):
                encrypted_data[field] = [encryption.encrypt(str(item)) for item in encrypted_data[field]]
    return encrypted_data

def decrypt_sensitive_cv_data(encrypted_cv_data: dict) -> dict:
    encryption = DataEncryption()
    sensitive_fields = [
        'name', 'email', 'phone', 'address',
        'personal_info', 'contact_details'
    ]
    decrypted_data = encrypted_cv_data.copy()
    for field in sensitive_fields:
        if field in decrypted_data and decrypted_data[field]:
            if isinstance(decrypted_data[field], str):
                decrypted_data[field] = encryption.decrypt(decrypted_data[field])
            elif isinstance(decrypted_data[field], list):
                decrypted_data[field] = [encryption.decrypt(str(item)) for item in decrypted_data[field]]
    return decrypted_data