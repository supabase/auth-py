import pytest


@pytest.fixture
def client():
    from gotrue import client

    return client.Client("http://localhost:9999")


def test_settings(client):
    res = client.settings()
    assert res.status_code == 200


def test_refresh_access_token():
    pass


@pytest.mark.incremental
class TestUserHandling:
    def test_signup(client):
        pass

    def test_login(client):
        pass

    def test_verify(client):
        pass

    def test_logout(self):
        pass


def test_send_magic_link(client):
    res = client.send_magic_link("someemail@gmail.com")
    assert res.status_code == 200 or res.status_code == 429


def test_recover_email(client):
    res = client.recover("someemail@gmail.com")
    assert res.status_code == 200 or res.status_code == 429
