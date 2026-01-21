def test_login_without_data(client):
    res = client.post("/login", json={})
    assert res.status_code == 400

def test_login_invalid_credentials(client):
    res = client.post("/login", json={
        "email": "fake@example.com",
        "password": "wrong"
    })
    assert res.status_code == 401