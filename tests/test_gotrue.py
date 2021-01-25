from gotrue import __version__
import pytest


@pytest.fixture
def client():
    from gotrue import client
    return client.Client(
        "https://distracted-elion-6bf6a2.netlify.app/.netlify/identity")


def test_version():
    assert __version__ == '0.1.0'


def test_signup():
    pass


def test_login():
    pass


def test_signout():
    pass


def test_settings(client):
    res = client.settings()
    assert (res.status_code == 200)


def test_refresh_access_token():
    pass