from cryptography.fernet import Fernet

# Generate a new encryption key
key = Fernet.generate_key()
print("Your encryption key:", key.decode())
# Run this code fiel to genrate it to see in the terminal
