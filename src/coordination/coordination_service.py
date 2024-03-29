from nltk.corpus import words
from src.password import Password, PydanticPassword
from src.coordination.big_job import BigJob
from src.password_breaking_agent.sub_job import StartJob, SubJob, StartJob, FinishJob
from pydantic import BaseModel
import time 
import logging  

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

DEFAULT_BATCH_SIZE = 2000
WORKER_EXPIRE_TIME = 60 * 2 #1 minutes

class Status(BaseModel):
  unfinished_big_jobs: list[str] = []
  finished_big_jobs: list[str] = []
  start_time: float |None = None
  end_time: float |None  = None
  total_time: float = None
  attempts_per_second: float = None
  total_attempts: int = None
  active_workers: int = None
  

class CoordinationService():
  _instance = None
  _initialized = False

  def __new__(cls, *args, **kwargs):
    if not cls._instance:
      cls._instance = super(CoordinationService, cls).__new__(cls)
    return cls._instance
  

  def __init__(self, pathToShadowFile: str, passwords_to_try: list[str], batch_size: int = DEFAULT_BATCH_SIZE) -> None:
    if CoordinationService._initialized:
      return 
    
    CoordinationService._initialized = True
    self.active_workers: dict[str, int] = {}

    self.pathToShadowFile = pathToShadowFile
    self.possible_passwords = passwords_to_try
    self.batch_size = batch_size
    self.unfinished_big_jobs: list[BigJob] = []
    self.generate_big_jobs()
    self.finished_big_jobs: list[BigJob] = []
    self.start_time = 0
    self.end_time = None 
    self.total_attempts = 0
    self.attempts_per_second = 0
    #mapping of worker id to time of last interaction, either a get_job or a finish_job
    
  
  def generate_big_jobs(self):
    passwords = Password.generatePasswordsFromFile(self.pathToShadowFile)
    for password in passwords:
      big_job = BigJob(password, self.possible_passwords, self.batch_size)
      self.unfinished_big_jobs.append(big_job) 
  
  def update_active_workers(self, worker_id: str | None) -> None:
    if worker_id is not None:
      self.active_workers[worker_id] = time.time()
    else :
      logger.error("Worker id is None")
    for worker_id, last_interaction in list(self.active_workers.items()):
      if time.time() - last_interaction > WORKER_EXPIRE_TIME:
        self.active_workers.pop(worker_id)
        logger.info(f"Worker {worker_id} expired")

  def get_job(self, worker_id: str | None) -> StartJob:
    #batch size is depricated
    self.update_active_workers(worker_id)
    if self.start_time == 0:
      self.start_time = time.time()
    sub_job = None
    for big_job in self.unfinished_big_jobs:
      sub_job = big_job.get_sub_job()
      if sub_job is not None:
        break
    if sub_job is None:
      return None
    return SubJob.subjob_to_startjob(sub_job)
  
  def update_attempts_per_second(self) -> None:
    self.attempts_per_second = self.total_attempts / (time.time() - self.start_time)
  
  def finish_job(self, job: FinishJob, worker_id: str | None) -> None:
    self.update_active_workers(worker_id)
    logger.info(f"Finishing job for user: {job.user}")
    pw_job = SubJob.finishjob_to_subjob(job)
    self.total_attempts += job.attempts
    self.update_attempts_per_second()
    big_job = self.get_big_job_by_id(pw_job.password.user)
    if big_job is None:
      logger.info('finishing job for already finished big job')
      return 
    big_job.finish_sub_job(pw_job)
    if big_job.is_finished():
      self.finished_big_jobs.append(big_job)
      self.unfinished_big_jobs.remove(big_job)
      self.spew_out_completed_jobs_to_file()
    if self.unfinished_big_jobs == []:
      self.end_time = time.time()
      
  def spew_out_completed_jobs_to_file(self):
    with open("finished_jobs.txt", "w") as file:
        for big_job in self.finished_big_jobs:
            file.write(f"=============\n{str(big_job)}\n=============\n\n") 


  def get_big_job_by_id(self, big_job_id: str) -> BigJob:
    for big_job in self.unfinished_big_jobs:
      if big_job.id == big_job_id:
        return big_job
    return None
  
  def get_status(self) -> Status:
    #map in progress jobs to start jobs
    #map finished jobs to finish jobs
    #map passwords to pydantic passwords
    total_time = self.end_time - self.start_time if self.end_time is not None else time.time() - self.start_time
    return Status(
      unfinished_big_jobs=[str(big_job) for big_job in self.unfinished_big_jobs],
      finished_big_jobs=[str(big_job) for big_job in self.finished_big_jobs],
      start_time=self.start_time,
      end_time=self.end_time,
      total_time=total_time,
      attempts_per_second=self.attempts_per_second,
      total_attempts=self.total_attempts,
      active_workers=len(self.active_workers)
    )





 


 

def get_coordination_service() -> CoordinationService:
  # return CoordinationService("fakeshadow2.txt",  words.words()[:500] + ["password1"] + words.words()[:500] + ["password2"] + words.words()[:500]  + ["password0"] + ["password3"] + ["password4"])
  return CoordinationService("hashed_passwords.txt",  words.words())