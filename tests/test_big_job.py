import pytest
from src.coordination.big_job import BigJob
from src.password_breaking_agent.pw_breaking_job import PwBreakingJob 
from src.password import Password

def test_generate_sub_jobs():
    password = Password('user1:$2b$12$wdqrbRHPmNQphg05t6wjjOfZGVYJrrzdD3//3nhFB1EVt6PJHNRDq')  # Replace with actual Password object
    passwords_to_try = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6']
    sub_job_size = 2

    big_job = BigJob(password, passwords_to_try, sub_job_size)
    sub_jobs = big_job.generate_sub_jobs(sub_job_size)

    # Check that the correct number of jobs was generated
    assert len(sub_jobs) == 3

    # Check that each job contains the correct number of passwords
    for job_id, job in sub_jobs.items():
        if job_id != 'job_2':
            assert len(job.pw_to_try) == sub_job_size
        else:
            # The last job may be smaller than sub_job_size
            assert len(job.pw_to_try) <= sub_job_size

    # Check that all passwords are covered by the jobs
    all_passwords_in_jobs = [password for job in sub_jobs.values() for password in job.pw_to_try]
    assert set(all_passwords_in_jobs) == set(passwords_to_try)

def test_big_job():
  password = Password('user1:$2b$12$wdqrbRHPmNQphg05t6wjjOfZGVYJrrzdD3//3nhFB1EVt6PJHNRDq')  # Replace with actual Password object
  passwords_to_try = ['random', 'another', 'weird', 'password1', 'password2', 'password3', 'password4', 'password5', 'password6']
  sub_job_size = 2

  big_job = BigJob(password, passwords_to_try, sub_job_size)

  # Test get_sub_job method
  job = big_job.get_sub_job()
  assert job in big_job.in_progress_jobs.values()

  # Test finish_sub_job method
  big_job.finish_sub_job(job)
  assert job not in big_job.in_progress_jobs.values()
  assert job in big_job.finished_jobs.values()

  #get the rest of the jobs
  rest_of_jobs = [big_job.get_sub_job() for i in range(3)]
  for job in rest_of_jobs:
      job.break_password()
      big_job.finish_sub_job(job)

  #make sure at least one of the rest_of_jobs has ['weird', 'password1'] as the pw_to_try
  assert any([job.pw_to_try == ['weird', 'password1'] for job in rest_of_jobs])

  assert big_job.end_time is not None
  assert big_job.unstarted_jobs == {}
  assert big_job.finished is True
  assert big_job.attempts > 2
  assert big_job.password.cracked_pw is not None 
  assert big_job.password.cracked_pw in passwords_to_try
  assert big_job.password.cracked_pw == 'password1'


def test_big_job_cannot_find():
  password = Password('user1:$2b$12$wdqrbRHPmNQphg05t6wjjOfZGVYJrrzdD3//3nhFB1EVt6PJHNRDq')  # Replace with actual Password object
  passwords_to_try = ['random', 'another', 'weird', 'password2', 'password3', 'password4', 'password5', 'password6']
  sub_job_size = 2

  big_job = BigJob(password, passwords_to_try, sub_job_size)

  #get the rest of the jobs
  rest_of_jobs = [big_job.get_sub_job() for i in range(5)]
  for job in rest_of_jobs:
    if job is not None:
      job.break_password()
      big_job.finish_sub_job(job)

  #make sure at least one of the rest_of_jobs has ['weird', 'password1'] as the pw_to_try

  assert big_job.end_time is not None
  assert big_job.unstarted_jobs == {}
  assert big_job.finished is True
  assert big_job.attempts == 8
  assert big_job.password.cracked_pw is None
   