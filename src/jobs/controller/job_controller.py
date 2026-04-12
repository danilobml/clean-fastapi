from fastapi import Request, HTTPException
from fastapi.routing import APIRouter
from starlette import status

from src.db.core import DbSession
from src.jobs.model.responses import JobResponse
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
    except Exception:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
