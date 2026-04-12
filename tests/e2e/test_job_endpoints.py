def test_get_all_jobs_endpoint(client, three_test_jobs):
    response = client.get("/jobs")

    body = response.json()

    job_ids = [job.get("id") for job in body]

    assert str(three_test_jobs[0].id) in job_ids
    assert str(three_test_jobs[1].id) in job_ids
    assert str(three_test_jobs[2].id) in job_ids
