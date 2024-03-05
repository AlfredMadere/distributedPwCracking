import pytest
from nltk.corpus import words
from src.coordination.coordination_service import CoordinationService
from src.password_breaking_agent.pw_breaking_job import PwBreakingJob, StartJob


def test_get_job():
    # Arrange
    coordination_service = CoordinationService("shadow.txt", words.words())

    # Act
    job = coordination_service.get_job(1000)

    # Assert
    assert job is not None, "Expected get_job to return a job, but it returned None"
    assert isinstance(job, StartJob), "Expected get_job to return a PwBreakingJob instance"

