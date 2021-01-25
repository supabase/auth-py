from gotrue import __version__
import pytest


@pytest.fixture
def client():
    from gotrue import client
    return client.Client("http://localhost:9999")


def test_settings(client):
    res = client.settings()
    assert (res.status_code == 200)


def test_refresh_access_token():
    pass


@pytest.mark.incremental
class TestUserHandling:
    def test_signup(client):
        pass

    def test_login(client):
        assert 1

    def test_verify(client):
        assert 1

    def test_logout(self):
        pass


def test_send_magic_link(client):
    res = client.send_magic_link("lee.yi.jie.joel@gmail.com")
    assert (res.status_code == 200 or res.status_code == 429)
