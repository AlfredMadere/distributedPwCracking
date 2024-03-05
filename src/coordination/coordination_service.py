
import queue
from src.password import Password, PydanticPassword
from src.password_breaking_agent.pw_breaking_job import PwBreakingJob, StartJob, FinishJob
import logging
from nltk.corpus import words
from pydantic import BaseModel
import time

logger = logging.getLogger(__name__)


class Status(BaseModel):
  num_in_progress_jobs: int = 0 
  num_finished_jobs: int  = 0 
  uncracked_passwords: list[PydanticPassword] = None
  cracked_passwords: list[PydanticPassword] = None
  start_time: float = None
  end_time: float = None

class CoordinationService:
  _instance = None
  _initialized = False

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = super(CoordinationService, cls).__new__(cls)
    return cls._instance

  def __init__(self, pathToShadowFile: str, passwords_to_try: list[str]) -> None:
    if CoordinationService._initialized:
      return

    CoordinationService._initialized = True
    logger.debug("Initializing coordination service")
    passwords = Password.generatePasswordsFromFile(pathToShadowFile)
    logger.info(f"Generated {len(passwords)} passwords from file")
    self.passwords = self.generate_pw_to_crack_queue(passwords)
    self.current_password = self.passwords.get()
    self.uncracked_passwords: dict[str, Password] = {}
    self.uncracked_passwords = {pw.user: pw for pw in passwords}
    self.possible_passwords = passwords_to_try
    self.pw_to_try_queue = self.generate_pw_to_try_queue(self.possible_passwords)
    self.cracked_passwords: dict[str, Password] = {}
    self.in_progress_jobs = {}
    self.finished_jobs = {}
    self.start_time = 0
    self.end_time = 0

  def generate_pw_to_try_queue(self, passwords_to_try: list[str]) -> queue.Queue:
    pw_to_try_queue = queue.Queue()
    for pw in passwords_to_try:
      pw_to_try_queue.put(pw)
    if pw_to_try_queue.empty():
      raise Exception("No passwords to try")
    return pw_to_try_queue

  def generate_pw_to_crack_queue(self, passwords) -> queue.Queue:
    pw_to_crack_queue = queue.Queue()
    for pw in passwords:
      pw_to_crack_queue.put(pw)
    return pw_to_crack_queue

  def get_job(self, num_passwords: int) -> StartJob :
    #check if there 
    #if we haven't started the timer, start it
    if self.start_time == 0:
      self.start_time = time.time()
    if self.pw_to_try_queue.empty():
      self.move_to_next_password()
    if self.current_password is None:
      return None

    job_passwords = []

    for _ in range(num_passwords):
      try: 
        job_passwords.append(self.pw_to_try_queue.get(False))
      except queue.Empty:
        break

    job = PwBreakingJob(self.current_password, job_passwords)

    self.in_progress_jobs[job.id] = job
    return PwBreakingJob.pw_job_to_startjob(job)

  def move_to_next_password(self) -> None:
    try: 
      #move the current password forward
      self.current_password = self.passwords.get(False)
      #reset the queue of passwords to try
      self.pw_to_try_queue = self.generate_pw_to_try_queue(self.possible_passwords) 
    except queue.Empty:
      logger.info("No more passwords to crack")
      self.current_password = None


  def finish_job(self, finish_job: FinishJob) -> None:
    job = PwBreakingJob.finish_job_to_pw_job(finish_job)
    self.in_progress_jobs.pop(job.id)
    self.finished_jobs[job.id] = job
    if self.uncracked_passwords.get(job.password.user) is None:
      logger.info(f"Password {job.password.user} is already cracked, not updating")
      return 
    
    self.update_passwords(job)
    if job.password.cracked_pw is not None:
      self.spew_cracked_passwords_to_file()
      self.move_to_next_password()

    if len(self.uncracked_passwords.items()) == 0:
      self.end_time = time.time()
    
  def spew_cracked_passwords_to_file(self) -> None:
    with open("cracked_passwords.txt", "w") as f:
      for pw in self.cracked_passwords.values():
        f.write(f"\n\n=============\n\n{str(pw)}\n\n=============\n\n")

  def update_passwords(self, job: PwBreakingJob) -> None: 
    if job.password.cracked_pw is not None:
      password = self.uncracked_passwords.pop(job.password.user)
      password.end_time = time.time()
      password.attempts += job.attempts
      password.cracked_pw = job.password.cracked_pw
      self.cracked_passwords[password.user] = password
    else:
      password = self.uncracked_passwords.pop(job.password.user)
      password.attempts += job.attempts
      self.uncracked_passwords[password.user] = password
     
    
  def get_status(self) -> Status:
    #map in progress jobs to start jobs
    #map finished jobs to finish jobs
    #map passwords to pydantic passwords
    for job in self.in_progress_jobs.values():
      logger.info(f"job id: {job.id} job: {job}")
    logger.info(f"current password is {self.current_password}")
    return Status(
      num_in_progress_jobs= len(self.in_progress_jobs.items()),#{str(job_id): PwBreakingJob.pw_job_to_startjob(job) for job_id, job in self.in_progress_jobs.items()},
      # in_progress_jobs={},
      num_finished_jobs= len(self.finished_jobs.items()),#{str(job_id): PwBreakingJob.finish_job_to_pw_job(job) for job_id, job in self.finished_jobs.items()},
      # finished_jobs={},
      uncracked_passwords=[Password.password_to_pydantic_password(pw) for pw in self.uncracked_passwords.values()],
      # uncracked_passwords=[],
      cracked_passwords=[Password.password_to_pydantic_password(pw) for pw in self.cracked_passwords.values()],
      # cracked_passwords=[],
      start_time=self.start_time,
      end_time=self.end_time,
    )


def get_coordination_service() -> CoordinationService:
  # return CoordinationService("fakeshadow2.txt",  words.words()[:500] + ["password1"] +  ["password2"] + ["password0"] + ["password3"] + ["password4"])
  return CoordinationService("shadow.txt",  words.words())
  # words.words()[:1000]  + words.words()[30000:400] +
