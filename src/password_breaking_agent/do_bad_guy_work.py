from src.password_breaking_agent.pw_breaking_job import PwBreakingJob, FinishJob
import requests
import logging

logger = logging.getLogger(__name__)
number_of_none_jobs = 0

while True: 
  if number_of_none_jobs > 10:
    logger.info("No more jobs to do")
    break
  job = None
  try:
    job = PwBreakingJob.get_job()
  except Exception as e:
    logger.error(f"Error getting job: {e}")
    continue
  if job is not None:
    logger.info(f"got a job {job.id} for user {job.password.user} with {len(job.pw_to_try)} passwords to try")
  if job is None:
    logger.debug("No job found")
    number_of_none_jobs += 1
    continue
  job.break_password()
  finished_job: FinishJob = job.convert_to_finish_job()

  #set a post request with the finished job to localhost:8000/coordination/finish_job
  response = requests.post("http://localhost:8000/coordination/finish_job", json=finished_job.model_dump())
  if response.status_code == 200:
    logger.info("Job finished successfully")
    if finished_job.password is not None:
      logger.info("Password cracked successfully for user: " + finished_job.user + " password: " + finished_job.password) 
  else:
    logger.info("Job failed to finish")

  
  
