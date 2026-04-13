from datetime import datetime, timedelta
from uuid import UUID

import pytest

from src.entities.job import Job, Priority
from src.errors.custom import UnauthorizedError
from src.jobs.model.requests import CreateJobRequest
from src.jobs.service import job_service


def test_get_all_jobs(three_test_jobs, db_session):
    jobs = job_service.get_all_jobs(db_session)

    job_descriptions = [job.description for job in jobs]

    assert three_test_jobs[0].description in job_descriptions
    assert three_test_jobs[1].description in job_descriptions
    assert three_test_jobs[2].description in job_descriptions


def test_create_job(_test_user, test_user_id, db_session):
    create_job_request = CreateJobRequest(
        user_id=UUID(test_user_id),
        description="Test job",
        due_date=datetime.now() + timedelta(days=2),
        priority=Priority.medium,
    )

    result = job_service.create_job(create_job_request, db_session)

    job = db_session.get(Job, result.id)

    assert job is not None
    assert job.id == result.id
    assert job.user_id == create_job_request.user_id
    assert job.description == create_job_request.description
    assert job.due_date == create_job_request.due_date
    assert job.priority == create_job_request.priority


def test_create_job_no_priority_passes_with_medium(
    _test_user, test_user_id, db_session
):
    create_job_request = CreateJobRequest(
        user_id=UUID(test_user_id),
        description="Test job",
        due_date=datetime.now() + timedelta(days=2),
    )

    result = job_service.create_job(create_job_request, db_session)

    job = db_session.get(Job, result.id)

    assert job is not None
    assert job.id == result.id
    assert job.user_id == create_job_request.user_id
    assert job.description == create_job_request.description
    assert job.due_date == create_job_request.due_date
    assert job.priority == Priority.medium


def test_create_job_missing_description_fails(_test_user, test_user_id, db_session):
    empty_description = ""
    create_job_request = CreateJobRequest(
        user_id=UUID(test_user_id),
        description=empty_description,
        due_date=datetime.now() + timedelta(days=2),
        priority=Priority.medium,
    )

    with pytest.raises(ValueError):
        job_service.create_job(create_job_request, db_session)


def test_create_job_nonexisting_user_id_fails(_test_user, db_session):
    nonexisting_user_id = "550e8400-e29b-41d4-a716-446655440000"
    create_job_request = CreateJobRequest(
        user_id=UUID(nonexisting_user_id),
        description="Test Job",
        due_date=datetime.now() + timedelta(days=2),
        priority=Priority.medium,
    )

    with pytest.raises(UnauthorizedError):
        job_service.create_job(create_job_request, db_session)
