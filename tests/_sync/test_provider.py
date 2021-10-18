import pytest

from gotrue import SyncGoTrueClient
from gotrue.types import Provider

GOTRUE_URL = "http://localhost:9999"


def create_client() -> SyncGoTrueClient:
    return SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    )


@pytest.mark.asyncio
def test_sign_in_with_provider():
    try:
        with create_client() as client:
            response = client.sign_in(provider=Provider.google)
            assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_a_redirect_url():
    try:
        with create_client() as client:
            response = client.sign_in(
                provider=Provider.google,
                redirect_to="https://localhost:9000/welcome",
            )
            assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_scopes():
    try:
        with create_client() as client:
            response = client.sign_in(provider=Provider.google, scopes="repo")
            assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_multiple_options():
    try:
        with create_client() as client:
            response = client.sign_in(
                provider=Provider.google,
                redirect_to="https://localhost:9000/welcome",
                scopes="repo",
            )
            assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)
