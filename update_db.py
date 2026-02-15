from supabase import create_client
import os
import encrypted, decrypt
import sys
import logging
import logging.handlers

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger_file_handler = logging.handlers.RotatingFileHandler(
    "mail.log",
    maxBytes=1024 * 1024,
    backupCount=1,
    encoding="utf8",
)
formatter = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
logger_file_handler.setFormatter(formatter)
logger.addHandler(logger_file_handler)

# Initialize client (same as your Streamlit app)
try:
  url = "https://oxsebytemqzoumgsrwgo.supabase.co" 
  SYPABASE_KEY = os.environ["SYPABASE_KEY"] 
  DECRYPTED_KEY = os.environ["DECRYPTED_KEY"]
  TABLE_NAME = "user_entries"
except:
  logger.error('SYPABASE_KEY/DECRYPTED_KEY not available!')

try:
    # Initialize Supabase client
    supabase = create_client(url, SYPABASE_KEY)
    
    # Fetch all data from the table
    response = supabase.table(TABLE_NAME)\
        .select("dob_key, name, email, emoji")\
        .execute()
    
    # Check if data exists
    if not response.data:
        print("empty db")
        sys.exit(0) 
    
    # Format the data as requested
    formatted_data = {}
    collect_mailid = []
    for entry in response.data:
        dob_key = entry['dob_key']
        formatted_data[dob_key] = {
            "name": entry['name'],
            "email": entry['email'],
            "emogi": entry['emoji']  
        }
        collect_mailid.append(entry['email'])
        logger.info(f"Entry added successfully for {entry['name']}")

    date_dict = decrypt.decrypt_database(str(DECRYPTED_KEY))

    # Added to existing db
    date_dict.update(formatted_data)
    print('succesfully updated!!')

    # Encrypting the db;
    encrypted.encrypt_db(DECRYPTED_KEY, date_dict)

    # Delete entry by Email-ID
    for email in collect_mailid:
        response = supabase.table("user_entries")\
            .delete()\
            .eq("email", email)\
            .execute()

    print(f"Deleted {len(collect_mailid)} row(s)")

except Exception as e:
    logger.error(e)
    
