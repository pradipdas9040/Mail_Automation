import streamlit as st
import json
from datetime import date
import decrypt, encrypted
import os

st.set_page_config(page_title="User Info to JSON", layout="centered")

st.title("🧾 User Details Form")

# -------- User Inputs --------
name = st.text_input("Name")

dob = st.date_input(
    "Date of Birth",
    min_value=date(1900, 1, 1),
    max_value=date.today()
)

email = st.text_input("Email ID")

emoji_list = ["😀", "😄", "🥳", "🎉", "🔥", "💡", "🚀", "❤️", "😎"]
emoji = st.selectbox("Select an Emoji", emoji_list)

# -------- Submit Button --------
if st.button("Generate JSON"):
    if name and email:
        dob_key = dob.strftime("%d-%m")  # MM-DD format

        result = {
            dob_key: {
                "name": name,
                "email": email,
                "emoji": emoji
            }
        }

        st.success("JSON Generated Successfully ✅")
        st.json(result)
        
        
        DECRYPTED_KEY = os.environ["DECRYPTED_KEY"]
        date_dict = decrypt.decrypt_database(str(DECRYPTED_KEY))

        ## Added to existing db
        date_dict.update(result)

        print(date_dict)
        print('succesfully updated!!')

        # Encrypting the db;
        encrypted.encrypt_db(DECRYPTED_KEY, date_dict)        

    else:
        st.error("Please fill in Name and Email ❌")
