def test_chatgpt_empty_message(client):
    with client.session_transaction() as sess:
        sess["logged_in"] = True
        sess["email"] = "test@example.com"

    res = client.post("/chatgpt", json={"message": ""})
    assert res.status_code == (400, 404)