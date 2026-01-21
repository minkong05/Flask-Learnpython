def login(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["email"] = "test@example.com"

def test_run_code_requires_login(client):
    res = client.post("/run_code", json={"code": "print(1)"})
    assert res.status_code in (401, 302)

def test_run_code_blocks_blacklisted_keywords(client):
    login(client)
    res = client.post("/run_code", json={"code": "import os"})
    assert res.status_code == 403

def test_run_code_rejects_large_payload(client):
    login(client)
    res = client.post("/run_code", json={"code": "A" * 5000})
    assert res.status_code == 413