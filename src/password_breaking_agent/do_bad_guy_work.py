from src.password_breaking_agent.sub_job import SubJob, FinishJob
import requests
import logging
import time
import random
import uuid

logger = logging.getLogger(__name__)
MAX_GET_JOB_ATTEMPTS = 50
num_no_job_available_attempts= 0
#string uuid
WORKER_ID = uuid.uuid4().__str__()

time.sleep(random.random() * 10)

while True: 
  if num_no_job_available_attempts > MAX_GET_JOB_ATTEMPTS:
    logger.info("No more jobs to do")
    break
  job = None
  try:
    #make a request to the coordination service to get a job
    job = SubJob.claim_job(WORKER_ID)
  except Exception as e:
    logger.error(f"Error getting job: {e}")
    time.sleep(5 +random.random() * 5)
    continue
  if job is not None:
    logger.info(f"got a job {job.id} for user {job.password.user} with {len(job.candidates)} passwords to try")
  if job is None:
    logger.debug("No job found")
    num_no_job_available_attempts += 1
    #wait 5 seconds before checking for jobs again
    time.sleep(5 + random.random() * 5)
    continue
  job.do_job(WORKER_ID)
  

  
  
