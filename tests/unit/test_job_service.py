from src.jobs.service import job_service


def test_get_all_jobs(three_test_jobs, db_session):
    jobs = job_service.get_all_jobs(db_session)

    job_descriptions = [job.description for job in jobs]

    assert three_test_jobs[0].description in job_descriptions
    assert three_test_jobs[1].description in job_descriptions
    assert three_test_jobs[2].description in job_descriptions
