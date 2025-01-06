from cryptography.fernet import Fernet

# Step 1: Generate a key and save it
key = Fernet.generate_key()

# Save the key to a file (you'll need this key to decrypt the file)
with open("secret.key", "wb") as key_file:
    key_file.write(key)

# Step 2: Initialize the Fernet class with the key
cipher = Fernet(key)

# Step 3: Read the original Python file
with open("data.py", "rb") as file:
    original_file_data = file.read()

# Step 4: Encrypt the data
encrypted_data = cipher.encrypt(original_file_data)

# Step 5: Save the encrypted data to a new file
with open("encrypted_database.enc", "wb") as encrypted_file:
    encrypted_file.write(encrypted_data)

print("File encrypted successfully!")
