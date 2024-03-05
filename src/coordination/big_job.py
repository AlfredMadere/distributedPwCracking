from src.password import Password
import time 
import logging
import queue 
from src.password_breaking_agent.pw_breaking_job import PwBreakingJob 
import itertools

logger = logging.getLogger(__name__)

class BigJob:
    def __init__(self, password: Password, passwords_to_try: list[str], sub_job_size: int) -> None:
      self.password = password
      self.id = password.user
      self.passwords_to_try = passwords_to_try 
      self.unstarted_jobs: dict[str, PwBreakingJob] = self.generate_sub_jobs(sub_job_size)
      self.in_progress_jobs: dict[str, PwBreakingJob] = {}
      self.finished_jobs: dict[str, PwBreakingJob] = {}
      self.attempts = 0
      self.start_time = 0
      self.end_time = 0
      self.finished = False


    def __str__(self) -> str:
      return f"BigJob for user: {self.password.user}\nStart time: {self.start_time}\nEnd time: {self.end_time}\nTotal time: {self.end_time - self.start_time} \nAttempts: {self.attempts}\nFinished: {self.finished}\nUnstarted jobs: {len(self.unstarted_jobs.items())}\nIn progress jobs: {len(self.in_progress_jobs.items())}\nFinished jobs: {len(self.finished_jobs)}\nPassword: {str(self.password)}"

    def generate_sub_jobs(self, sub_job_size: int) -> dict[str, PwBreakingJob]:
      sub_jobs = {}
      for i in range(0, len(self.passwords_to_try), sub_job_size):
          chunk = self.passwords_to_try[i:i+sub_job_size]
          job = PwBreakingJob(self.password, chunk)
          sub_jobs[job.id] = job
      return sub_jobs
    
    def is_finished(self) -> bool:
      return self.finished

    def get_sub_job(self) -> PwBreakingJob:
      if self.start_time == 0:
        self.start_time = time.time()
      if len(self.unstarted_jobs) == 0:
        if(len(self.in_progress_jobs.items()) == 0):
          self.expire_old_jobs()
        return None
      job_id, job = self.unstarted_jobs.popitem()
      self.in_progress_jobs[job_id] = job
      return job
    
    def expire_old_jobs(self) -> None:
      #for every job in in_progress_jobs, check if its expired and if it is move it back to unstarted_jobs
      for job_id, job in list(self.in_progress_jobs.items()):
        if job.is_expired():
          self.unstarted_jobs[job_id] = job
          self.in_progress_jobs.pop(job_id)
          logger.info(f"Job {job_id} expired")

    def finish_sub_job(self, job: PwBreakingJob) -> None:
      logger.info(f"Finishing sub job {job.id}, {job.password.cracked_pw}")
      self.in_progress_jobs.pop(job.id)
      self.finished_jobs[job.id] = job
      self.attempts += job.attempts
      if job.password.cracked_pw is not None:
        self.password.cracked_pw = job.password.cracked_pw
        self.whole_job_finished()
      if self.in_progress_jobs == {} and self.unstarted_jobs == {}:
        self.whole_job_finished()
        logger.info("All jobs finished")

    def whole_job_finished(self) -> None:
      self.end_time = time.time()
      self.finished = True
      self.unstarted_jobs = {}


    def generate_pw_to_try_queue(self, passwords_to_try: list[str]) -> queue.Queue:
      pw_to_try_queue = queue.Queue()
      for pw in passwords_to_try:
        pw_to_try_queue.put(pw)
      if pw_to_try_queue.empty():
        raise Exception("No passwords to try")
      return pw_to_try_queue