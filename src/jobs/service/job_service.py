from sqlalchemy.orm import Session

from src.entities.job import Job, Priority
from src.entities.user import User
from src.errors.custom import UnauthorizedError
from src.jobs.model.requests import CreateJobRequest
from src.jobs.model.responses import CreateJobResponse


def get_all_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()


def create_job(request: CreateJobRequest, db: Session) -> CreateJobResponse:
    if request.description == "":
        raise ValueError("description must be non-empty")

    user = db.get(User, request.user_id)
    if not user:
        raise UnauthorizedError()

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
