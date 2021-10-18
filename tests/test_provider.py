import pytest

from gotrue import AsyncGoTrueClient
from gotrue.common.types import Provider

client = AsyncGoTrueClient(auto_refresh_token=False, persist_session=False)


@pytest.mark.asyncio
async def test_sign_in_with_provider():
    response = await client.sign_in(provider=Provider.google)
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_sign_in_with_provider_can_append_a_redirect_url():
    response = await client.sign_in(
        provider=Provider.google,
        redirect_to="https://localhost:9000/welcome",
    )
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_sign_in_with_provider_can_append_scopes():
    response = await client.sign_in(provider=Provider.google, scopes="repo")
    assert isinstance(response, str)


@pytest.mark.asyncio
async def test_sign_in_with_provider_can_append_multiple_options():
    response = await client.sign_in(
        provider=Provider.google,
        redirect_to="https://localhost:9000/welcome",
        scopes="repo",
    )
    assert isinstance(response, str)
