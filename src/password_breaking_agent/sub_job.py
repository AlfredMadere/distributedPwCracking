
from bcrypt import hashpw, gensalt
from src.password import Password
import logging
import time
import multiprocessing
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor
import concurrent.futures
import uuid
from pydantic import BaseModel
import requests


logger = logging.getLogger(__name__)
num_cores = multiprocessing.cpu_count()
logger.info(f"Number of cores: {num_cores}")

class StartJob(BaseModel):
  bcrypt_salt: str = None
  pw_hash: str = None
  passwords_to_try: list[str] = None
  user: str = None
  job_id: str = None

class FinishJob(StartJob):
  password: str | None = None
  start_time: float = None
  end_time: float = None
  attempts: int = None
  pw_per_second: float = None



MAX_JOB_TIME = 60 * 5 #5 minutes

class SubJob:
  def __init__(self, password: Password, pw_to_try: list[str], id: str | None = None) -> None:
    self.password = password
    if id is not None:
      self.id = uuid.UUID(id)
    else: 
      self.id = uuid.uuid4()
    self.candidates = pw_to_try
    self.start_time = 0
    self.end_time = 0
    self.attempts = 0
    self.candidates_per_second = 0

  def is_expired(self) -> bool:
    if self.start_time == 0:
      return False
    return time.time() - self.start_time > MAX_JOB_TIME

  def hash_pw(self, pw: str) -> str:
    logger.debug(f"Hashing password {pw}")
    logger.debug(f"Salt: {self.password.bcrypt_salt}")
    encoded_pw = pw.encode()
    encoded_salt = self.password.bcrypt_salt.encode()
    logger.debug(f"Encoded password: {encoded_pw}")
    logger.debug(f"Encoded salt: {encoded_salt}")
    hashed_pw = hashpw(encoded_pw, encoded_salt)
    logger.debug(f"Hashed password: {hashed_pw}")
    return hashed_pw.decode()
  
  def try_candidates(self) -> str | None :
    logger.info(f"Breaking password for user: {self.password.user}")
    self.start_time = time.time()
    for pw in self.candidates:
      if self.attempts is None:
        self.attempts = 0
      self.attempts += 1
      hashed_pw = self.hash_pw(pw)
      # logger.info(f"Hashed password: {hashed_pw}, original hash: {self.password.bcrypt_salt + self.password.hash}")
      # logger.info(f"Comparing {hashed_pw} to {self.password.bcrypt_salt + self.password.hash}, they are equal: {hashed_pw == (self.password.bcrypt_salt + self.password.hash)}")
      # logger.info(f"Byte comparison: {hashed_pw.encode() == (self.password.bcrypt_salt + self.password.hash).encode()}")
      # logger.info(f"the types are {type(hashed_pw)} and {type(self.password.bcrypt_salt + self.password.hash)} respectively")
      # logger.info(f"Repr comparison: {repr(hashed_pw)} vs {repr(self.password.bcrypt_salt + self.password.hash)}")
      if hashed_pw == (self.password.bcrypt_salt + self.password.hash):
        self.end_time = time.time()
        self.candidates_per_second = 10# self.attempts / (self.end_time - self.start_time)
        self.password.cracked_pw = pw
        logger.info(f"Password cracked: {pw}")
        return pw
    logger.info(f"Password not found")
    self.end_time = time.time()
    return None
  
  def convert_to_finish_job(self) -> FinishJob:
    return FinishJob(
      bcrypt_salt=self.password.bcrypt_salt,
      pw_hash=self.password.hash,
      passwords_to_try=self.candidates,
      user=self.password.user,
      password=self.password.cracked_pw,
      start_time=self.start_time,
      end_time=self.end_time,
      attempts=self.attempts,
      pw_per_second=10,
      job_id=str(self.id)
    )

  @classmethod
  def subjob_to_startjob(cls, job: 'SubJob') -> StartJob:
    return StartJob(
      bcrypt_salt=job.password.bcrypt_salt,
      pw_hash=job.password.hash,
      passwords_to_try=job.candidates,
      user=job.password.user,
      job_id=str(job.id)
    )

  @classmethod
  def finishjob_to_subjob(cls, job: FinishJob) -> 'SubJob':
    password = Password(f"{job.user}:{job.bcrypt_salt}{job.pw_hash}")
    password.cracked_pw = job.password
    pw_breakingjob = SubJob(
      password=password,
      id=job.job_id,
      pw_to_try=job.passwords_to_try,
   )
    pw_breakingjob.start_time=job.start_time
    pw_breakingjob.end_time=job.end_time
    pw_breakingjob.attempts=job.attempts
    pw_breakingjob.candidates_per_second=job.pw_per_second
    return pw_breakingjob

  def monitor_progress(self) -> None:
    #while break_password is running, update the time it has taken + number of attempts + rate of attempts
    pass


  @classmethod
  def startjob_to_subjob(cls, job: StartJob) -> 'SubJob':
    password_constrction_str = f"{job.user}:{job.bcrypt_salt}{job.pw_hash}"
    password = Password(password_constrction_str)
    logger.info(f"Creating job for user: {password_constrction_str}")
    pw_breakingjob = SubJob(
      password=password,
      id=job.job_id,
      pw_to_try=job.passwords_to_try,
   )
    return pw_breakingjob

  @classmethod
  def claim_job(cls, worker_id) -> 'SubJob':
    #make a call out to localhost:8000/coordination/get_job, return the response
    headers = {
      "worker_id": worker_id
    }
    response = requests.get("http://localhost:8000/coordination/get_job", headers=headers)
    #convert the response to a PwBreakingJob
    if response.status_code == 401:
      return None
    if response.status_code != 200:
      raise Exception(f"Failed to get job: {response.status_code}")
    job = SubJob.startjob_to_subjob(StartJob.model_validate(response.json()))
    #if the response is a 401, return None
   
    return job
  
  def do_job(self, worker_id) -> None:
    self.try_candidates()
    finished_job = self.convert_to_finish_job()
    response = requests.post("http://localhost:8000/coordination/finish_job", json=finished_job.model_dump(), headers={"worker_id": worker_id})
    if response.status_code == 200:
      logger.info("Job finished successfully")
    if finished_job.password is not None:
      logger.info("Password cracked successfully for user: " + finished_job.user + " password: " + finished_job.password) 
    else:
      logger.info("Job failed to be recorded as finished")

