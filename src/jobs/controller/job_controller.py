from uuid import UUID

from fastapi import Request, HTTPException
from fastapi.routing import APIRouter
from sqlalchemy.exc import NoResultFound
from starlette import status

from src.db.core import DbSession
from src.errors.custom import AlreadyCompletedError, NonexistingUserError
from src.jobs.model.requests import CreateJobRequest, UpdateJobRequest
from src.jobs.model.responses import CompleteJobResponse, CreateJobResponse, JobResponse
from src.rate_limiting import limiter
from src.jobs.service import job_service
from src.security.jwt import CurrentUser


job_router = APIRouter(prefix="/jobs")


@job_router.get("/", status_code=status.HTTP_200_OK, response_model=list[JobResponse])
@limiter.limit("5/hour")
async def get_all_jobs(
    request: Request, db: DbSession, _current_user: CurrentUser
) -> list[JobResponse]:
    try:
        jobs = job_service.get_all_jobs(db)
        return [
            JobResponse(
                id=job.id,
                user_id=job.user_id,
                description=job.description,
                due_date=job.due_date,
                priority=job.priority,
                is_completed=job.is_completed,
            )
            for job in jobs
        ]
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"{e}"
        )


@job_router.post(
    "/", status_code=status.HTTP_201_CREATED, response_model=CreateJobResponse
)
@limiter.limit("5/hour")
async def create_job(
    request: Request,
    create_job_request: CreateJobRequest,
    db: DbSession,
    _current_user: CurrentUser,
) -> CreateJobResponse:
    try:
        return job_service.create_job(create_job_request, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except NoResultFound as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"{e}")


@job_router.patch(
    "/{id}/complete", status_code=status.HTTP_200_OK, response_model=CompleteJobResponse
)
@limiter.limit("5/hour")
async def complete_job(
    request: Request, id: UUID, db: DbSession, _current_user: CurrentUser
) -> CompleteJobResponse:
    try:
        return job_service.complete_job(id, db)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    except AlreadyCompletedError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")


@job_router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
@limiter.limit("5/hour")
async def delete_job(
    request: Request, id: UUID, db: DbSession, _current_user: CurrentUser
) -> None:
    try:
        job_service.delete_job(id, db)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )


@job_router.put("/{id}", status_code=status.HTTP_200_OK, response_model=JobResponse)
@limiter.limit("5/hour")
async def update_job(
    request: Request,
    id: UUID,
    update_job_request: UpdateJobRequest,
    db: DbSession,
    _current_user: CurrentUser,
) -> JobResponse:
    try:
        return job_service.update_job(id, update_job_request, db)
    except NoResultFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Job not found"
        )
    except NonexistingUserError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="User with this user_id doesn't exist",
        )
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
