from src.password_breaking_agent.sub_job import SubJob, FinishJob
import requests
import logging
import time

logger = logging.getLogger(__name__)
MAX_GET_JOB_ATTEMPTS = 10
num_no_job_available_attempts= 0

while True: 
  if num_no_job_available_attempts > MAX_GET_JOB_ATTEMPTS:
    logger.info("No more jobs to do")
    break
  job = None
  try:
    #make a request to the coordination service to get a job
    job = SubJob.claim_job()
  except Exception as e:
    logger.error(f"Error getting job: {e}")
    continue
  if job is not None:
    logger.info(f"got a job {job.id} for user {job.password.user} with {len(job.candidates)} passwords to try")
  if job is None:
    logger.debug("No job found")
    num_no_job_available_attempts += 1
    #wait 5 seconds before checking for jobs again
    time.sleep(5)
    continue
  job.try_candidates()
  #All candidates have been hashed, convert the job to a pydantic FinishJob model which includes important informatino about the job including whether it cracked the password
  finished_job: FinishJob = job.convert_to_finish_job()
  #send a post request with the finished job to localhost:8000/coordination/finish_job - port forwarding will send this request to the coordination service
  response = requests.post("http://localhost:8000/coordination/finish_job", json=finished_job.model_dump())
  #Below is just for debugging 
  if response.status_code == 200:
    logger.info("Job finished successfully")
    if finished_job.password is not None:
      logger.info("Password cracked successfully for user: " + finished_job.user + " password: " + finished_job.password) 
  else:
    logger.info("Job failed to be recorded as finished")

  
  
