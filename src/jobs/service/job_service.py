from uuid import UUID

from sqlalchemy import delete, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from src.entities.job import Job, Priority
from src.entities.user import User
from src.errors.custom import AlreadyCompletedError
from src.jobs.model.requests import CreateJobRequest
from src.jobs.model.responses import CompleteJobResponse, CreateJobResponse


def get_all_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()


def create_job(request: CreateJobRequest, db: Session) -> CreateJobResponse:
    if request.description == "":
        raise ValueError("description must be non-empty")

    user = db.get(User, request.user_id)
    if not user:
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
        raise NoResultFound()

    raise AlreadyCompletedError()


def delete_job(id: UUID, db: Session) -> None:
    deleted_count = db.query(Job).filter(Job.id == id).delete()

    if deleted_count == 1:
        db.commit()
        return

    raise NoResultFound()
