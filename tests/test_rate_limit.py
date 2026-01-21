def test_chatgpt_requires_login(client):
    res = client.post("/chatgpt", json={"message": "hi"})
    assert res.status_code in (401, 302)

def test_chatgpt_rejects_long_input(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["email"] = "test@example.com"

    long_message = "A" * 1000
    res = client.post("/chatgpt", json={"message": long_message})
    assert res.status_code in (400, 404)