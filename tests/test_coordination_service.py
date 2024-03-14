import pytest
from src.coordination.coordination_service import CoordinationService
from src.password_breaking_agent.sub_job import SubJob, StartJob, FinishJob

def test_generate_big_jobs():
    path_to_shadow_file = 'shadow.txt'  # Replace with actual path
    possible_passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6']
    batch_size = 2

    service = CoordinationService(path_to_shadow_file, possible_passwords, batch_size)
    service.generate_big_jobs()
    assert len(service.unfinished_big_jobs) > 0

def test_get_job():
    path_to_shadow_file = 'shadow.txt'  # Replace with actual path
    possible_passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6']
    batch_size = 2

    service = CoordinationService(path_to_shadow_file, possible_passwords, batch_size)
    start_job = service.get_job()
    assert isinstance(start_job, StartJob)  # Replace with actual StartJob class

def test_finish_job():
    path_to_shadow_file = 'shadow.txt'  # Replace with actual path
    possible_passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password6']
    batch_size = 2

    service = CoordinationService(path_to_shadow_file, possible_passwords, batch_size)
    start_job = service.get_job()
    job = SubJob.startjob_to_subjob(start_job)
    job.try_candidates()
    finish_job = SubJob.convert_to_finish_job(job) 
    service.finish_job(finish_job)
    assert service.unfinished_big_jobs[0].attempts == 2

def test_finish_job_crack():
    path_to_shadow_file = 'fakeshadow.txt'  # Replace with actual path 
    # possible_passwords = ['password1', 'password2', 'password3', 'password4', 'password5', 'password0', 'password6']
    possible_passwords = ['it blows', 'so bad', 'registrationsucks'] 
    service = CoordinationService(path_to_shadow_file, possible_passwords, 3)
    for i in range(4):
        start_job = service.get_job()
        if start_job is None:
            break 
        job = SubJob.startjob_to_subjob(start_job)
        job.try_candidates()
        finish_job = SubJob.convert_to_finish_job(job)
        service.finish_job(finish_job)
    assert service.finished_big_jobs[0].password.cracked_pw == 'registrationsucks'  
    assert service.finished_big_jobs[0].attempts == 3
    assert service.end_time is not None
    assert service.unfinished_big_jobs == []
    assert service.finished_big_jobs != []
    # Add assertions to check the state of the service after finishing a job