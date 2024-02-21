from cryptography.fernet import Fernet

key = b'Krta2hU60ea8gIpJXCWMNQaz6-4x4SH9g3skBafJ6rk='
cipher = Fernet(key)


def encrypt(value):
    encrypted_value = cipher.encrypt(value.encode('utf-8')).decode('utf-8')
    print("Encrypted Value = ",encrypted_value)
    return encrypted_value


def decrypt(encrypted_value):
    decrypted_value = cipher.decrypt(encrypted_value.encode('utf-8')).decode('utf-8')
    print("Decrypted Value = ",decrypted_value)
    return decrypted_value


encrypt('961a57166796e968c2a82cbf1657926dd76cd9829921d0660e8266a475067bb6') #django secret key
