from typing import Iterable

import pytest

from gotrue import SyncGoTrueClient
from gotrue.types import Provider

GOTRUE_URL = "http://localhost:9999"


@pytest.fixture(name="client")
def create_client() -> Iterable[SyncGoTrueClient]:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


@pytest.mark.asyncio
def test_sign_in_with_provider(client: SyncGoTrueClient):
    try:
        response = client.sign_in(provider=Provider.google)
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_a_redirect_url(
    client: SyncGoTrueClient,
):
    try:
        response = client.sign_in(
            provider=Provider.google,
            redirect_to="https://localhost:9000/welcome",
        )
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_scopes(client: SyncGoTrueClient):
    try:
        response = client.sign_in(provider=Provider.google, scopes="repo")
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_provider_can_append_multiple_options(
    client: SyncGoTrueClient,
):
    try:
        response = client.sign_in(
            provider=Provider.google,
            redirect_to="https://localhost:9000/welcome",
            scopes="repo",
        )
        assert isinstance(response, str)
    except Exception as e:
        assert False, str(e)
