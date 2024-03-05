from src.password import Password
from src.password_breaking_agent.pw_breaking_job import PwBreakingJob
import pytest
import nltk 
nltk.download('words')
from nltk.corpus import words

def test_password_breaking_service():
    shadow_str = "Bilbo:$2b$08$J9FW66ZdPI2nrIMcOxFYI.zKGJsUXmWLAYWsNmIANUy5JbSjfyLFu"
    password = Password(shadow_str)
    possible_passwords = ["registrationsucks"]
    password_breaker = PwBreakingJob(password, possible_passwords)
    broken_password = password_breaker.break_password()
    assert broken_password == "registrationsucks"

def test_pw_b_service_real():
    shadow_str = "Bilbo:$2b$08$J9FW66ZdPI2nrIMcOxFYI.zKGJsUXmWLAYWsNmIANUy5JbSjfyLFu"
    password = Password(shadow_str)
    possible_passwords = words.words()[:4] + ["registrationsucks"] 
    assert len(possible_passwords) == 5
    password_breaker = PwBreakingJob(password, possible_passwords)
    broken_password = password_breaker.break_password()
    assert broken_password == "registrationsucks"

def test_convert_to_finish_job():
    shadow_str = "Bilbo:$2b$08$J9FW66ZdPI2nrIMcOxFYI.zKGJsUXmWLAYWsNmIANUy5JbSjfyLFu"
    password = Password(shadow_str)
    possible_passwords = ["registrationsucks"]
    password_breaker = PwBreakingJob(password, possible_passwords)
    broken_password = password_breaker.break_password()
    finished_job = password_breaker.convert_to_finish_job()
    assert finished_job.password == "registrationsucks"
    assert finished_job.bcrypt_salt == password.bcrypt_salt
    assert finished_job.pw_hash == password.hash
    assert finished_job.user == password.user
    assert finished_job.start_time == password_breaker.start_time
    assert finished_job.end_time == password_breaker.end_time
    assert finished_job.attempts == password_breaker.attempts
    assert finished_job.pw_per_second == 10
    assert finished_job.job_id == str(password_breaker.id)

def test_words_length():
    assert len(words.words()) == 236736

@pytest.mark.skip(reason="long running ")
def test_first_shadow():
    shadow_str = "Bilbo:$2b$08$J9FW66ZdPI2nrIMcOxFYI.qx268uZn.ajhymLP/YHaAsfBGP3Fnmq"
    password = Password(shadow_str)
    possible_passwords = words.words()
    password_breaker = PwBreakingJob(password, possible_passwords)
    broken_password = password_breaker.break_password()
    assert broken_password != "NOT FOUND"
    #write the broken password to a new file
    with open("broken_passwords.txt", "w") as f:
        f.write(broken_password)



