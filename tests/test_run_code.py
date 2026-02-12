import pytest
from unittest.mock import patch


def login(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["email"] = "test@example.com"


def test_run_code_requires_login(client):
    res = client.post("/run_code", json={"code": "print(1)"})
    assert res.status_code in (401, 302)


def test_run_code_rejects_large_payload(client):
    login(client)
    res = client.post("/run_code", json={"code": "A" * 5000})
    assert res.status_code == 413


@patch("requests.post")
def test_run_code_success(mock_post, client):
    login(client)

    mock_post.return_value.status_code = 200
    mock_post.return_value.json.return_value = {
        "output": "2\n",
        "error": ""
    }

    res = client.post("/run_code", json={"code": "print(1+1)"})

    assert res.status_code == 200
    data = res.get_json()
    assert data["output"] == "2\n"


@patch("requests.post")
def test_run_code_sandbox_timeout(mock_post, client):
    login(client)

    mock_post.return_value.status_code = 408
    mock_post.return_value.json.return_value = {
        "error": "Execution timeout"
    }

    res = client.post("/run_code", json={"code": "while True: pass"})

    assert res.status_code == 408


@patch("requests.post")
def test_run_code_sandbox_error(mock_post, client):
    login(client)

    mock_post.return_value.status_code = 500
    mock_post.return_value.json.return_value = {
        "error": "Sandbox failure"
    }

    res = client.post("/run_code", json={"code": "bad code"})

    assert res.status_code == 500

