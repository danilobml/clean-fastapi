import logging
from uuid import UUID

from sqlalchemy import update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.entities.job import Job, Priority
from src.entities.user import User
from src.errors.custom import AlreadyCompletedError, DBError, NonexistingUserError
from src.jobs.model.requests import CreateJobRequest, UpdateJobRequest
from src.jobs.model.responses import CompleteJobResponse, CreateJobResponse, JobResponse


def get_all_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()


def create_job(request: CreateJobRequest, db: Session) -> CreateJobResponse:
    if request.description == "":
        raise ValueError("description must be non-empty")

    user = db.get(User, request.user_id)
    if not user:
        logging.warning(f"No user found with id {request.user_id}")
        raise NoResultFound()

    new_job = Job(
        user_id=request.user_id,
        description=request.description,
        due_date=request.due_date,
        priority=request.priority or Priority.medium,
    )

    db.add(new_job)
    db.commit()
    db.refresh(new_job)

    return CreateJobResponse(
        id=new_job.id,
        user_id=new_job.user_id,
        description=new_job.description,
        due_date=new_job.due_date,
        priority=new_job.priority,
    )


def complete_job(job_id: UUID, db: Session) -> CompleteJobResponse:
    result = db.execute(
        update(Job)
        .where(Job.id == job_id, Job.is_completed.is_(False))
        .values(is_completed=True)
    )

    if result.rowcount == 1:  # type: ignore[attr-defined]
        db.commit()
        return CompleteJobResponse(message="Job successfully completed")

    job = db.get(Job, job_id)

    if not job:
        logging.warning(f"No job found with id {job_id}")
        raise NoResultFound()

    logging.warning(f"Attempted to complete already completed job with id {job_id}")
    raise AlreadyCompletedError()


def delete_job(job_id: UUID, db: Session) -> None:
    deleted_count = db.query(Job).filter(Job.id == job_id).delete()

    if deleted_count == 1:
        db.commit()
        return

    logging.warning(f"No job found with id {job_id}")
    raise NoResultFound()


def update_job(
    job_id: UUID, update_job_request: UpdateJobRequest, db: Session
) -> JobResponse:
    job = db.get(Job, job_id)
    if not job:
        logging.warning(f"No job found with id {job_id}")
        raise NoResultFound()

    if update_job_request.user_id:
        user = db.get(User, update_job_request.user_id)
        if not user:
            logging.warning(f"No user found with id {update_job_request.user_id}")
            raise NonexistingUserError()

    new_user_id = update_job_request.user_id or job.user_id
    new_description = (
        update_job_request.description
        if (update_job_request.description and update_job_request.description != "")
        else job.description
    )
    new_due_date = update_job_request.due_date or job.due_date
    new_priority = update_job_request.priority or job.priority

    result = db.execute(
        update(Job)
        .where(Job.id == job_id)
        .values(
            user_id=new_user_id,
            description=new_description,
            due_date=new_due_date,
            priority=new_priority,
        )
    )

    if result.rowcount == 1:  # type: ignore[attr-defined]
        db.commit()
        db.refresh(job)
    else:
        logging.warning(f"Failed DB operation at update job with id {job_id}")
        raise DBError()

    return JobResponse(
        id=job.id,
        user_id=job.user_id,
        description=job.description,
        due_date=job.due_date,
        priority=job.priority,
        is_completed=job.is_completed,
    )
