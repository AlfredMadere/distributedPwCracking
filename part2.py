import re
from src.password import Password
from pw_breaking_service import PwBreakingService
import nltk 
nltk.download('words')
from nltk.corpus import words


def break_passwords_from_file(file):
    with open(file, 'r') as f:
        pws = f.readlines()
    for pw in pws:
        password_breaker = PwBreakingService(Password(pw), words.words())
        broken_password = password_breaker.break_password()


shadow_entries = break_passwords_from_file('shadow.txt')


for entry in shadow_entries:
    print(entry)
