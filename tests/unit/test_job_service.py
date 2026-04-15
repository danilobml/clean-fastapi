from datetime import datetime, timedelta
from uuid import UUID

import pytest
from sqlalchemy.exc import NoResultFound

from src.entities.job import Job, Priority
from src.errors.custom import AlreadyCompletedError, NonexistingUserError
from src.jobs.model.requests import CreateJobRequest, UpdateJobRequest
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

    with pytest.raises(NoResultFound):
        job_service.create_job(create_job_request, db_session)


def test_complete_job(test_job, db_session):
    job_service.complete_job(test_job.id, db_session)

    job = db_session.get(Job, test_job.id)

    assert job.is_completed is True


def test_complete_nonexisting_job_fails(db_session):
    nonexisting_job_id = "c9f7a9b1-8b8a-4b0e-9c2f-6d4d2f7c5e13"

    with pytest.raises(NoResultFound):
        job_service.complete_job(UUID(nonexisting_job_id), db_session)


def test_complete_already_completed_job_fails(three_test_jobs, db_session):
    completed_job = three_test_jobs[1]

    with pytest.raises(AlreadyCompletedError):
        job_service.complete_job(completed_job.id, db_session)


def test_delete_job(test_job, db_session):
    job_service.delete_job(test_job.id, db_session)

    job = db_session.get(Job, test_job.id)

    assert job is None


def test_delete_nonexisting_job_fails(db_session):
    nonexisting_job_id = "c9f7a9b1-8b8a-4b0e-9c2f-6d4d2f7c5e13"

    with pytest.raises(NoResultFound):
        job_service.delete_job(UUID(nonexisting_job_id), db_session)


def test_update_job(_two_users, test_job, db_session):
    job_id = test_job.id
    new_user_id = _two_users[1].id
    new_description = "Updated description"
    new_due_date = datetime.now() + timedelta(days=3)
    new_priority = Priority.high

    update_job_request = UpdateJobRequest(
        user_id=new_user_id,
        description=new_description,
        due_date=new_due_date,
        priority=new_priority,
    )

    updated_job = job_service.update_job(job_id, update_job_request, db_session)

    assert updated_job.user_id == new_user_id
    assert updated_job.description == new_description
    assert updated_job.due_date == new_due_date
    assert updated_job.priority == new_priority


def test_update_job_partial_update(test_job, _test_user, db_session):
    job_id = test_job.id
    new_description = "Updated description"

    update_job_request = UpdateJobRequest(
        description=new_description,
    )

    updated_job = job_service.update_job(job_id, update_job_request, db_session)

    assert updated_job.user_id == test_job.user_id
    assert updated_job.description == new_description
    assert updated_job.due_date == test_job.due_date
    assert updated_job.priority == test_job.priority


def test_update_nonexisting_job_fails(db_session):
    nonexisting_job_id = "c9f7a9b1-8b8a-4b0e-9c2f-6d4d2f7c5e13"
    new_description = "Updated description"

    update_job_request = UpdateJobRequest(
        description=new_description,
    )

    with pytest.raises(NoResultFound):
        job_service.update_job(UUID(nonexisting_job_id), update_job_request, db_session)


def test_update_job_nonexisting_user_fails(test_job, db_session):
    job_id = test_job.id
    nonexisting_user_id = "c9f7a9b1-8b8a-4b0e-9c2f-6d4d2f7c5e13"
    new_description = "Updated description"
    new_due_date = datetime.now() + timedelta(days=3)
    new_priority = Priority.high

    update_job_request = UpdateJobRequest(
        user_id=UUID(nonexisting_user_id),
        description=new_description,
        due_date=new_due_date,
        priority=new_priority,
    )

    with pytest.raises(NonexistingUserError):
        job_service.update_job(job_id, update_job_request, db_session)
