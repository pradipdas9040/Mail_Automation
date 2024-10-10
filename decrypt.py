from cryptography.fernet import Fernet

def decrypt_database(key):
    try:
        # Step 1: encode key from str to bytes
        key = key.encode("utf-8")

        # Step 2: Initialize the Fernet class with the key
        cipher = Fernet(key)

        # Step 3: Read the encrypted file
        with open("encrypted_database.enc", "rb") as encrypted_file:
            encrypted_data = encrypted_file.read()

        # Step 4: Decrypt the data
        decrypted_data = cipher.decrypt(encrypted_data)

        # Step 5: Define a local context (dictionary) to store variables after execution
        local_context = {}

        # Step 6: Execute the decrypted Python code in the provided context
        exec(decrypted_data.decode(), {}, local_context)
        return local_context['return_info']()
    
    except Exception as e:
        raise e
