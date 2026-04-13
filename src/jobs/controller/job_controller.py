from fastapi import Request, HTTPException
from fastapi.routing import APIRouter
from starlette import status

from src.db.core import DbSession
from src.errors.custom import UnauthorizedError
from src.jobs.model.requests import CreateJobRequest
from src.jobs.model.responses import CreateJobResponse, JobResponse
from src.rate_limiting import limiter
from src.jobs.service import job_service


job_router = APIRouter(prefix="/jobs")


@job_router.get("/", status_code=status.HTTP_200_OK, response_model=list[JobResponse])
@limiter.limit("5/hour")
async def get_all_jobs(request: Request, db: DbSession) -> list[JobResponse]:
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
    request: Request, create_job_request: CreateJobRequest, db: DbSession
) -> CreateJobResponse:
    try:
        return job_service.create_job(create_job_request, db)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")
    except UnauthorizedError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=f"{e}")
