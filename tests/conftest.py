import pytest
from app import app as flask_app

@pytest.fixture
def app():
    flask_app.config.update({
        "TESTING": True,
        "WTF_CSRF_ENABLED": False,  # disable CSRF in tests
        "SECRET_KEY": "test-secret"
    })
    return flask_app

@pytest.fixture
def client(app):
    return app.test_client()