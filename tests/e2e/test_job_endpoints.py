from starlette import status

from src.jobs.model.responses import JobResponse


def test_get_all_jobs_endpoint(client, three_test_jobs):
    response = client.get("/jobs")

    body = response.json()

    job_ids = []
    for job in body:
        assert JobResponse(**job)
        job_ids.append(job.get("id"))

    assert response.status_code == status.HTTP_200_OK
    assert str(three_test_jobs[0].id) in job_ids
    assert str(three_test_jobs[1].id) in job_ids
    assert str(three_test_jobs[2].id) in job_ids


def test_create_job_endpoint(client, _test_user, test_user_id):
    user_id = test_user_id
    description = "Test Job"
    due_date = "2026-04-14T15:42:10.123456"
    priority = "medium"

    response = client.post(
        "/jobs",
        json={
            "user_id": user_id,
            "description": description,
            "due_date": due_date,
            "priority": priority,
        },
    )

    body = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert body.get("user_id") == user_id
    assert body.get("description") == description
    assert body.get("due_date") == due_date
    assert body.get("priority") == priority


def test_create_job_endpoint_no_priority_passes_with_medium(
    client, _test_user, test_user_id
):
    user_id = test_user_id
    description = "Test Job"
    due_date = "2026-04-14T15:42:10.123456"
    default_priority = "medium"

    response = client.post(
        "/jobs",
        json={"user_id": user_id, "description": description, "due_date": due_date},
    )

    body = response.json()

    assert response.status_code == status.HTTP_201_CREATED
    assert body.get("user_id") == user_id
    assert body.get("description") == description
    assert body.get("due_date") == due_date
    assert body.get("priority") == default_priority


def test_create_job_invalid_user_id_fails(client):
    user_id = "123"
    description = "Test Job"
    due_date = "2026-04-14T15:42:10.123456"
    priority = "medium"

    response = client.post(
        "/jobs",
        json={
            "user_id": user_id,
            "description": description,
            "due_date": due_date,
            "priority": priority,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_job_invalid_due_date_fails(client, test_user_id):
    user_id = test_user_id
    description = "Test Job"
    due_date = "02.03.2026"
    priority = "medium"

    response = client.post(
        "/jobs",
        json={
            "user_id": user_id,
            "description": description,
            "due_date": due_date,
            "priority": priority,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_job_invalid_priority_fails(client, test_user_id):
    user_id = test_user_id
    description = "Test Job"
    due_date = "2026-04-14T15:42:10.123456"
    priority = "super"

    response = client.post(
        "/jobs",
        json={
            "user_id": user_id,
            "description": description,
            "due_date": due_date,
            "priority": priority,
        },
    )

    assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


def test_create_job_nonexisting_user_fails(client):
    nonexisting_user_id = "550e8400-e29b-41d4-a716-446655440000"
    description = "Test Job"
    due_date = "2026-04-14T15:42:10.123456"
    priority = "medium"

    response = client.post(
        "/jobs",
        json={
            "user_id": nonexisting_user_id,
            "description": description,
            "due_date": due_date,
            "priority": priority,
        },
    )

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_complete_job_endpoint(client, test_job):
    response = client.patch(f"/jobs/{str(test_job.id)}/complete")

    body = response.json()

    assert response.status_code == status.HTTP_200_OK
    assert body.get("message") == "Job successfully completed"

    get_response = client.get("/jobs")
    get_body = get_response.json()

    assert get_response.status_code == status.HTTP_200_OK

    completed_job = next(job for job in get_body if job.get("id") == str(test_job.id))
    assert JobResponse(**completed_job)
    assert completed_job.get("is_completed") is True


def test_complete_nonexisting_job_fails(client):
    nonexisting_job_id = "c9f7a9b1-8b8a-4b0e-9c2f-6d4d2f7c5e13"

    response = client.patch(f"/jobs/{nonexisting_job_id}/complete")

    assert response.status_code == status.HTTP_404_NOT_FOUND


def test_complete_already_completed_job_fails(client, three_test_jobs):
    completed_job = three_test_jobs[1]
    response = client.patch(f"/jobs/{str(completed_job.id)}/complete")

    body = response.json()

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert body.get("detail") == "This job is already completed"


def test_delete_job_endpoint(client, test_job):
    response = client.delete(f"/jobs/{str(test_job.id)}")

    assert response.status_code == status.HTTP_204_NO_CONTENT

    get_response = client.get("/jobs")
    get_body = get_response.json()

    assert get_response.status_code == status.HTTP_200_OK

    job_ids = [job.get("id") for job in get_body]
    assert str(test_job.id) not in job_ids
def test_delete_nonexisting_job_fails(client):
    nonexisting_job_id = "c9f7a9b1-8b8a-4b0e-9c2f-6d4d2f7c5e13"

    response = client.delete(f"/jobs/{nonexisting_job_id}")

    assert response.status_code == status.HTTP_404_NOT_FOUND
