from pydantic import BaseModel
import bcrypt
import logging

logger = logging.getLogger(__name__)
# logger.setLevel(logging.DEBUG)

class PydanticPassword(BaseModel):
  user: str = None
  bcrypt_salt: str = None
  hash: str = None
  cracked_pw: str | None = None
  start_time: float = None
  end_time: float = None
  attempts: int = None

class Password:
  def __init__(self, shadow_str: str) -> None:
    self.cracked_pw: str | None = None
    self.start_time = 0
    self.end_time = 0
    self.attempts = 0
    self.parse_shadow_string(shadow_str)

  def __str__(self) -> str:
    return f"User: {self.user} \n Bcrypt Salt: {self.bcrypt_salt} \n Hash: {self.hash} \n Cracked Password: {self.cracked_pw} \n "

  def parse_shadow_string(self, shadow_str: str) -> None:
    #Everything before ":" is the user
    #The format is "User:$Algorithm$WorkFactor$SaltHash"
    #The salt is the first 22 characters of the salt hash, the hash is the rest
    #now parse the shadow_str
    split_str = shadow_str.split(":")
    self.user = split_str[0]
    salt_hash = split_str[1]
    #the first 22 characters of the salt hash are the salt, the rest are the hash
    self.bcrypt_salt = salt_hash[:29]
    self.hash = salt_hash[29:]

  @staticmethod
  def generatePasswordsFromFile(filename: str) -> list['Password']:
    passwords = []
    with open(filename, "r") as f:
      for line in f:
        passwords.append(Password(line.strip()))
    return passwords
  
  @staticmethod
  def password_to_pydantic_password(password: 'Password') -> PydanticPassword:
    return PydanticPassword(user=password.user, bcrypt_salt=password.bcrypt_salt, hash=password.hash, cracked_pw=password.cracked_pw, start_time=password.start_time, end_time=password.end_time, attempts=password.attempts)


  @staticmethod
  def generate_password_string(username: str, password: str) -> str:
    salt = bcrypt.gensalt()
    logger.debug(f"Generated salt: {salt}")
    hashed = bcrypt.hashpw(password.encode(), salt)
    logger.debug(f"Generated hash: {hashed}")
    shadow_str = f"{username}:{hashed.decode()}"
    logger.debug(f"Generated shadow string: {shadow_str}")
    return shadow_str

  @staticmethod
  def generate_fake_shadow_file():
    with open("fakeshadow2.txt", "w") as f:
      for i in range(5):
        str =Password.generate_password_string(f"user{i}", f"password{i}")
        f.write(str + "\n")
        


