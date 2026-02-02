def test_login_without_data(client):
    res = client.post("/login", json={})
    assert res.status_code == 400

    data = res.get_json()
    assert data["message"] == "No data received"

def test_login_invalid_credentials(client):
    res = client.post("/login", json={
        "email": "fake@example.com",
        "password": "wrong"
    })
    assert res.status_code == 401


def test_login_missing_password(client):
    res = client.post("/login", json={
        "email": "test@example.com"
    })
    assert res.status_code == 400

    data = res.get_json()
    assert data["message"] == "Email or password missing"