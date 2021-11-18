from typing import AsyncIterable

import pytest

from gotrue import AsyncGoTrueClient
from gotrue.types import Provider

GOTRUE_URL = "http://localhost:9999"


@pytest.fixture(name="client")
async def create_client() -> AsyncIterable[AsyncGoTrueClient]:
    async with AsyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


@pytest.mark.asyncio
async def test_sign_in_with_provider(client: AsyncGoTrueClient):
    try:
        response = await client.sign_in(provider=Provider.google)
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
async def test_sign_in_with_provider_can_append_a_redirect_url(
    client: AsyncGoTrueClient,
):
    try:
        response = await client.sign_in(
            provider=Provider.google,
            redirect_to="https://localhost:9000/welcome",
        )
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
async def test_sign_in_with_provider_can_append_scopes(client: AsyncGoTrueClient):
    try:
        response = await client.sign_in(provider=Provider.google, scopes="repo")
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
async def test_sign_in_with_provider_can_append_multiple_options(
    client: AsyncGoTrueClient,
):
    try:
        response = await client.sign_in(
            provider=Provider.google,
            redirect_to="https://localhost:9000/welcome",
            scopes="repo",
        )
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)
