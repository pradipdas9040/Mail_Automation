from cryptography.fernet import Fernet
import pprint
import os

def write_data_py(date_dict, file_path="data.py"):
    with open(file_path, "w", encoding="utf-8") as f:
        f.write("def return_info():\n")
        f.write("    date_dict = ")

        # Pretty-print dict with indentation
        formatted_dict = pprint.pformat(date_dict, indent=8, width=80)

        # Indent dict correctly inside function
        indented_dict = formatted_dict.replace("\n", "\n    ")

        f.write(indented_dict + "\n")
        f.write("    return date_dict\n")

def encrypt_db(key, data):
    key_bytes = key.encode("utf-8")
    # Step 2: Initialize the Fernet class with the key
    cipher = Fernet(key_bytes)

    ## Creating the temporary data.py file with the updated dictionary;
    write_data_py(data)

    # Step 3: Read the original Python file
    with open("data.py", "rb") as file:
        original_file_data = file.read()

    # Step 4: Encrypt the data
    encrypted_data = cipher.encrypt(original_file_data)

    # Step 5: Save the encrypted data to a new file
    with open("encrypted_database.enc", "wb") as encrypted_file:
        encrypted_file.write(encrypted_data)
        
    ## deleting the temporary data.py file
    
    file_path = "data.py"

    if os.path.exists(file_path):
        os.remove(file_path)
        print("✅ data.py deleted successfully")
    else:
        print("ℹ️ data.py does not exist")    
    

    print("File encrypted successfully!")
