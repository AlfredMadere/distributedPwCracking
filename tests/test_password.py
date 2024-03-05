import pytest
from src.password import Password
import bcrypt
def test_password_init():
    shadow_str = "Bilbo:$2b$08$J9FW66ZdPI2nrIMcOxFYI.zKGJsUXmWLAYWsNmIANUy5JbSjfyLFu"
    password = Password(shadow_str)
    assert password.user == "Bilbo"
    assert password.bcrypt_salt == "$2b$08$J9FW66ZdPI2nrIMcOxFYI."
    assert password.hash == "zKGJsUXmWLAYWsNmIANUy5JbSjfyLFu"

def test_generate_passwords_from_file(tmp_path):
    d = tmp_path / "sub"
    d.mkdir()
    p = d / "shadow.txt"
    p.write_text("user1:$1$work_factor1$salt_hash1\nuser2:$1$work_factor2$salt_hash2")
    passwords = Password.generatePasswordsFromFile(str(p))
    assert len(passwords) == 2
    assert passwords[0].user == "user1"
    assert passwords[1].user == "user2"

def test_generate_password_string():
    username = 'Bilbo'
    password = 'mypassword'

    # Call the static method
    result = Password.generate_password_string(username, password)

    # Check that the result is a string
    assert isinstance(result, str)

    # Check that the result is in the correct format
    username_result, hashed_password = result.split(':')
    

    assert username_result == username

    # Check that the hashed password can be verified with the original password
    assert bcrypt.checkpw(password.encode(), hashed_password.encode())

def test_generate_fake_shadow_file():
    Password.generate_fake_shadow_file()
    passwords = Password.generatePasswordsFromFile("fakeshadow2.txt")
    assert len(passwords) == 5
    assert passwords[0].user == "user0"
    assert passwords[1].user == "user1"
    assert passwords[2].user == "user2"
    assert passwords[3].user == "user3"
    assert passwords[4].user == "user4"
    

@pytest.mark.skip(reason="Only runs from the command line")
def test_ingest_shadow_file():
    passwords = Password.generatePasswordsFromFile("shadow.txt")
    assert len(passwords) == 15
    assert passwords[0].user == "Bilbo" 


