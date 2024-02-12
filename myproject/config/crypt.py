from cryptography.fernet import Fernet

key = b'Krta2hU60ea8gIpJXCWMNQaz6-4x4SH9g3skBafJ6rk='
cipher = Fernet(key)


def encrypt(value):
    encrypted_value = cipher.encrypt(value.encode('utf-8')).decode('utf-8')
    print(encrypted_value)
    return encrypted_value


def decrypt(encrypted_value):
    decrypted_value = cipher.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
    print(decrypted_value)
    return decrypted_value


encrypt('techlab')
