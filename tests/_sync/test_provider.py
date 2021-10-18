import pytest

from gotrue import SyncGoTrueClient
from gotrue.types import Provider

client = SyncGoTrueClient(auto_refresh_token=False, persist_session=False)


@pytest.mark.asyncio
def test_sign_in_with_provider():
    response = client.sign_in(provider=Provider.google)
    assert isinstance(response, str)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_a_redirect_url():
    response = client.sign_in(
        provider=Provider.google,
        redirect_to="https://localhost:9000/welcome",
    )
    assert isinstance(response, str)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_scopes():
    response = client.sign_in(provider=Provider.google, scopes="repo")
    assert isinstance(response, str)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_multiple_options():
    response = client.sign_in(
        provider=Provider.google,
        redirect_to="https://localhost:9000/welcome",
        scopes="repo",
    )
    assert isinstance(response, str)
