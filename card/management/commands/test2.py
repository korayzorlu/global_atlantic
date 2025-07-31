import random
import string

characters = string.ascii_letters + string.digits
version = ''.join(random.choice(characters) for _ in range(8))

print(version)