

import bcrypt
import nltk
import random
from nltk.corpus import words

# Ensure the word corpus is downloaded
nltk.download('words')

# Initialize the word list
word_list = words.words()

# Open a file to write the hashed passwords
with open("hashed_passwords.txt", "w") as file:
    for i in range(1, 11):
        # Generate a random username for demonstration
        username = f"user{i}"
        
        # Select a random word to use as the password
        password = random.choice(word_list).encode('utf-8')
        
        # Hash the password using bcrypt with a work factor of 10
        hashed_password = bcrypt.hashpw(password, bcrypt.gensalt(rounds=10))
        
        # Decode the hashed password to a UTF-8 string and extract components for formatting
        # Note: Direct decoding and formatting to match the expected pattern
        hashed_str = hashed_password.decode('utf-8')
        
        # Write the formatted hashed password to the file
        file.write(f"{username}:$2b$10${hashed_str.split('$')[-1]}\n")

print("Hashed passwords have been written to hashed_passwords.txt")