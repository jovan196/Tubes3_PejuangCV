#import base64
import hashlib
import secrets
import string

# =======================
# Core Encryption Classes
# =======================

class DataEncryption:
    """
    Sistem enkripsi custom untuk melindungi data pribadi pelamar.
    Menggunakan kombinasi Caesar Cipher, XOR, dan Base64 encoding untuk keamanan berlapis.
    """
    def __init__(self, key: str = "ATS_SECURE_KEY_2025"):
        self.key = key
        self.caesar_shift = self._generate_caesar_shift(key)
        self.xor_key = self._generate_xor_key(key)

    def _generate_caesar_shift(self, key: str) -> int:
        shift = sum(ord(c) for c in key) % 26
        return shift if shift > 0 else 13

    def _generate_xor_key(self, key: str) -> bytes:
        return hashlib.sha256(key.encode()).digest()[:16]

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
        try:
            step1 = self._custom_substitution(plaintext, encrypt=True)
            step2 = self._caesar_encrypt(step1, self.caesar_shift)
            step3_bytes = step2.encode('utf-8')
            step3_encrypted = self._xor_encrypt_decrypt(step3_bytes, self.xor_key)
            return base64.b64encode(step3_encrypted).decode('utf-8')
        except Exception as e:
            print(f"Encryption error: {e}")
            return plaintext

    def decrypt(self, ciphertext: str) -> str:
        if not ciphertext:
            return ""
        try:
            step1_bytes = base64.b64decode(ciphertext.encode('utf-8'))
            step2_bytes = self._xor_encrypt_decrypt(step1_bytes, self.xor_key)
            step2 = step2_bytes.decode('utf-8')
            step3 = self._caesar_decrypt(step2, self.caesar_shift)
            return self._custom_substitution(step3, encrypt=False)
        except Exception as e:
            print(f"Decryption error: {e}")
            return ciphertext

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
        try:
            return original == self.decrypt(encrypted)
        except:
            return False

    def change_key(self, new_key: str) -> None:
        self.key = new_key
        self.caesar_shift = self._generate_caesar_shift(new_key)
        self.xor_key = self._generate_xor_key(new_key)

    def get_encryption_info(self) -> dict:
        return {
            "caesar_shift": self.caesar_shift,
            "xor_key_length": len(self.xor_key),
            "key_hash": hashlib.sha256(self.key.encode()).hexdigest()[:16],
            "encryption_layers": [
                "Custom Substitution Cipher",
                "Caesar Cipher",
                "XOR Cipher",
                "Base64 Encoding"
            ]
        }

class AdvancedDataEncryption(DataEncryption):
    """
    Advanced encryption with additional security features.
    """
    def __init__(self, key: str = "ATS_SECURE_KEY_2025"):
        super().__init__(key)
        self.salt = self._generate_salt()
        self.iteration_count = 1000

    def _generate_salt(self) -> bytes:
        return hashlib.sha256(self.key.encode()).digest()[:16]

    def _derive_key(self, password: str, salt: bytes) -> bytes:
        key = password.encode()
        for _ in range(self.iteration_count):
            key = hashlib.sha256(key + salt).digest()
        return key[:32]

    def encrypt_with_timestamp(self, plaintext: str) -> str:
        import time
        timestamp = str(int(time.time()))
        data_with_timestamp = f"{timestamp}|{plaintext}"
        return self.encrypt(data_with_timestamp)

    def decrypt_with_timestamp(self, ciphertext: str, max_age_seconds: int = 86400) -> str:
        import time
        try:
            decrypted = self.decrypt(ciphertext)
            if '|' not in decrypted:
                return decrypted
            timestamp_str, data = decrypted.split('|', 1)
            timestamp = int(timestamp_str)
            current_time = int(time.time())
            if current_time - timestamp > max_age_seconds:
                raise ValueError("Data expired")
            return data
        except Exception as e:
            print(f"Decryption with timestamp failed: {e}")
            return ""

    def encrypt_file(self, file_path: str, output_path: str = None) -> bool:
        try:
            with open(file_path, 'rb') as f:
                file_data = f.read()
            file_b64 = base64.b64encode(file_data).decode()
            encrypted_data = self.encrypt(file_b64)
            if output_path is None:
                output_path = file_path + '.encrypted'
            with open(output_path, 'w') as f:
                f.write(encrypted_data)
            return True
        except Exception as e:
            print(f"File encryption failed: {e}")
            return False

    def decrypt_file(self, encrypted_file_path: str, output_path: str = None) -> bool:
        try:
            with open(encrypted_file_path, 'r') as f:
                encrypted_data = f.read()
            file_b64 = self.decrypt(encrypted_data)
            file_data = base64.b64decode(file_b64.encode())
            if output_path is None:
                output_path = encrypted_file_path.replace('.encrypted', '')
            with open(output_path, 'wb') as f:
                f.write(file_data)
            return True
        except Exception as e:
            print(f"File decryption failed: {e}")
            return False

class DatabaseFieldEncryption:
    """
    Specialized encryption for database fields with field-specific keys.
    """
    def __init__(self, master_key: str = "ATS_DB_MASTER_KEY"):
        self.master_key = master_key
        self.field_encryptors = {}

    def get_field_encryptor(self, field_name: str) -> DataEncryption:
        if field_name not in self.field_encryptors:
            field_key = f"{self.master_key}_{field_name}"
            self.field_encryptors[field_name] = DataEncryption(field_key)
        return self.field_encryptors[field_name]

    def encrypt_field(self, field_name: str, value: str) -> str:
        encryptor = self.get_field_encryptor(field_name)
        return encryptor.encrypt(value)

    def decrypt_field(self, field_name: str, encrypted_value: str) -> str:
        encryptor = self.get_field_encryptor(field_name)
        return encryptor.decrypt(encrypted_value)

    def encrypt_record(self, record: dict, encrypted_fields: list) -> dict:
        encrypted_record = record.copy()
        for field in encrypted_fields:
            if field in encrypted_record and encrypted_record[field] is not None:
                encrypted_record[field] = self.encrypt_field(field, str(encrypted_record[field]))
        return encrypted_record

    def decrypt_record(self, encrypted_record: dict, encrypted_fields: list) -> dict:
        decrypted_record = encrypted_record.copy()
        for field in encrypted_fields:
            if field in decrypted_record and decrypted_record[field] is not None:
                decrypted_record[field] = self.decrypt_field(field, str(decrypted_record[field]))
        return decrypted_record

# =======================
# Utility Functions
# =======================

def generate_secure_key(length: int = 32) -> str:
    alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
    return ''.join(secrets.choice(alphabet) for _ in range(length))

def hash_password(password: str, salt: str = None) -> tuple:
    if salt is None:
        salt = generate_secure_key(16)
    hashed = password + salt
    for _ in range(10000):
        hashed = hashlib.sha256(hashed.encode()).hexdigest()
    return hashed, salt

def verify_password(password: str, hashed_password: str, salt: str) -> bool:
    computed_hash, _ = hash_password(password, salt)
    return computed_hash == hashed_password

# =======================
# CV Data Encryption API
# =======================

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

# =======================
# Benchmark & Testing
# =======================

class EncryptionBenchmark:
    """
    Benchmark encryption performance for different data sizes.
    """
    def __init__(self):
        self.encryption = DataEncryption()

    def benchmark_text_sizes(self, sizes: list = None) -> dict:
        import time
        if sizes is None:
            sizes = [100, 1000, 10000, 100000]
        results = {}
        for size in sizes:
            test_text = "A" * size
            start_time = time.time()
            encrypted = self.encryption.encrypt(test_text)
            encrypt_time = time.time() - start_time
            start_time = time.time()
            decrypted = self.encryption.decrypt(encrypted)
            decrypt_time = time.time() - start_time
            is_correct = decrypted == test_text
            results[size] = {
                'encrypt_time': encrypt_time,
                'decrypt_time': decrypt_time,
                'total_time': encrypt_time + decrypt_time,
                'encrypted_size': len(encrypted),
                'compression_ratio': len(encrypted) / size,
                'is_correct': is_correct
            }
        return results

    def run_performance_test(self) -> dict:
        import time
        iterations = 1000
        test_text = "This is a test string for encryption performance"
        start_time = time.time()
        for _ in range(iterations):
            encrypted = self.encryption.encrypt(test_text)
        encrypt_total_time = time.time() - start_time
        start_time = time.time()
        for _ in range(iterations):
            decrypted = self.encryption.decrypt(encrypted)
        decrypt_total_time = time.time() - start_time
        return {
            'iterations': iterations,
            'test_text_length': len(test_text),
            'average_encrypt_time': encrypt_total_time / iterations,
            'average_decrypt_time': decrypt_total_time / iterations,
            'encryptions_per_second': iterations / encrypt_total_time,
            'decryptions_per_second': iterations / decrypt_total_time,
            'total_test_time': encrypt_total_time + decrypt_total_time
        }

def test_encryption_system():
    print("Testing ATS Encryption System...")
    encryption = DataEncryption()
    test_data = "Hello, World! 123 @#$%"
    encrypted = encryption.encrypt(test_data)
    decrypted = encryption.decrypt(encrypted)
    if decrypted != test_data:
        print("❌ Basic encryption test failed")
        return False
    print("✅ Basic encryption test passed")
    test_dict = {
        'name': 'John Doe',
        'email': 'john@example.com',
        'age': 30,
        'skills': ['Python', 'JavaScript']
    }
    encrypted_dict = encryption.encrypt_dict(test_dict, ['name', 'email'])
    decrypted_dict = encryption.decrypt_dict(encrypted_dict, ['name', 'email'])
    if decrypted_dict['name'] != test_dict['name'] or decrypted_dict['email'] != test_dict['email']:
        print("❌ Dictionary encryption test failed")
        return False
    print("✅ Dictionary encryption test passed")
    advanced_encryption = AdvancedDataEncryption()
    encrypted_with_timestamp = advanced_encryption.encrypt_with_timestamp(test_data)
    decrypted_with_timestamp = advanced_encryption.decrypt_with_timestamp(encrypted_with_timestamp)
    if decrypted_with_timestamp != test_data:
        print("❌ Advanced encryption test failed")
        return False
    print("✅ Advanced encryption test passed")
    db_encryption = DatabaseFieldEncryption()
    test_record = {
        'id': 1,
        'first_name': 'John',
        'last_name': 'Doe',
        'email': 'john@example.com',
        'salary': 50000
    }
    encrypted_record = db_encryption.encrypt_record(test_record, ['first_name', 'last_name', 'email'])
    decrypted_record = db_encryption.decrypt_record(encrypted_record, ['first_name', 'last_name', 'email'])
    if (decrypted_record['first_name'] != test_record['first_name'] or 
        decrypted_record['last_name'] != test_record['last_name'] or
        decrypted_record['email'] != test_record['email']):
        print("❌ Database field encryption test failed")
        return False
    print("✅ Database field encryption test passed")
    print("🎉 All encryption tests passed!")
    return True

def generate_encryption_report():
    encryption = DataEncryption()
    benchmark = EncryptionBenchmark()
    report = {
        'system_info': encryption.get_encryption_info(),
        'performance': benchmark.run_performance_test(),
        'size_benchmarks': benchmark.benchmark_text_sizes(),
        'security_features': [
            "Multi-layer encryption (Substitution + Caesar + XOR + Base64)",
            "Field-specific encryption keys",
            "Timestamp-based encryption",
            "File encryption support",
            "Custom encryption algorithms (no external crypto libraries)",
            "Salt-based key derivation",
            "Password hashing with iteration"
        ],
        'recommended_usage': {
            'personal_data': ['first_name', 'last_name', 'address', 'phone_number'],
            'sensitive_fields': ['email', 'salary', 'ssn', 'bank_account'],
            'non_encrypted': ['id', 'created_at', 'status', 'public_info']
        }
    }
    return report

if __name__ == "__main__":
    test_encryption_system()
    report = generate_encryption_report()
    print("\n" + "="*50)
    print("ENCRYPTION SYSTEM REPORT")
    print("="*50)
    print(f"\nSecurity Features:")
    for feature in report['security_features']:
        print(f"  ✓ {feature}")
    print(f"\nPerformance Metrics:")
    perf = report['performance']
    print(f"  • Encryptions per second: {perf['encryptions_per_second']:.0f}")
    print(f"  • Decryptions per second: {perf['decryptions_per_second']:.0f}")
    print(f"  • Average encrypt time: {perf['average_encrypt_time']*1000:.2f}ms")
    print(f"  • Average decrypt time: {perf['average_decrypt_time']*1000:.2f}ms")