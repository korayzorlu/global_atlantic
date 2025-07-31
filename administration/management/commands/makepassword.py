import random
import string

def generate_password(length, special_chars):
    characters = string.ascii_letters + string.digits + special_chars
    password = ''.join(random.choice(characters) for i in range(length))
    return password

password_length = 8
allowed_special_chars = "!%&*.:"
password = generate_password(password_length,allowed_special_chars)
print("Üretilen şifre:", password)