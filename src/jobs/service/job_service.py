from sqlalchemy.orm import Session

from src.entities.job import Job


def get_all_jobs(db: Session) -> list[Job]:
    return db.query(Job).all()
