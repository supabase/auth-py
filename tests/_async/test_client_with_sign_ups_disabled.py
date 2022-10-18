from typing import AsyncIterable

import pytest
from faker import Faker

from ...gotrue import AsyncGoTrueAPI, AsyncGoTrueClient
from ...gotrue.constants import COOKIE_OPTIONS, DEFAULT_HEADERS
from ...gotrue.errors import APIError
from ...gotrue.types import CookieOptions, GenerateLinkType, User, UserAttributes

GOTRUE_URL = "http://localhost:9997"
AUTH_ADMIN_TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InN1cGFiYXNlX2FkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.0sOtTSTfPv5oPZxsjvBO249FI4S4p0ymHoIZ6H6z9Y8"  # noqa: E501


@pytest.fixture(name="auth_admin")
async def create_auth_admin() -> AsyncIterable[AsyncGoTrueAPI]:
    async with AsyncGoTrueAPI(
        url=GOTRUE_URL,
        headers={"Authorization": f"Bearer {AUTH_ADMIN_TOKEN}"},
        cookie_options=CookieOptions.parse_obj(COOKIE_OPTIONS),
    ) as api:
        yield api


@pytest.fixture(name="client")
async def create_client() -> AsyncIterable[AsyncGoTrueClient]:
    async with AsyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


fake = Faker()

email = fake.email().lower()
password = fake.password()


async def test_sign_up(client: AsyncGoTrueClient):
    expected_error_message = "Signups not allowed for this instance"
    try:
        await client.sign_up(email=email, password=password)
        assert False
    except APIError as e:
        assert e.msg == expected_error_message
    except Exception as e:
        assert False, str(e)


invited_user = fake.email().lower()


async def test_generate_link_should_be_able_to_generate_multiple_links(
    auth_admin: AsyncGoTrueAPI,
):
    try:
        response = await auth_admin.generate_link(
            type=GenerateLinkType.invite,
            email=invited_user,
            redirect_to="http://localhost:9997",
        )
        assert isinstance(response, User)
        assert response.email == invited_user
        assert response.action_link
        assert "http://localhost:9997/?token=" in response.action_link
        assert response.app_metadata
        assert response.app_metadata.get("provider") == "email"
        providers = response.app_metadata.get("providers")
        assert providers
        assert isinstance(providers, list)
        assert len(providers) == 1
        assert providers[0] == "email"
        assert response.role == ""
        assert response.user_metadata == {}
        assert response.identities == []
        user = response
        response = await auth_admin.generate_link(
            type=GenerateLinkType.invite,
            email=invited_user,
        )
        assert isinstance(response, User)
        assert response.email == invited_user
        assert response.action_link
        assert "http://localhost:9997/?token=" in response.action_link
        assert response.app_metadata
        assert response.app_metadata.get("provider") == "email"
        providers = response.app_metadata.get("providers")
        assert providers
        assert isinstance(providers, list)
        assert len(providers) == 1
        assert providers[0] == "email"
        assert response.role == ""
        assert response.user_metadata == {}
        assert response.identities == []
        user_again = response
        assert user.id == user_again.id
    except Exception as e:
        assert False, str(e)


email2 = fake.email().lower()


async def test_create_user(auth_admin: AsyncGoTrueAPI):
    try:
        attributes = UserAttributes(email=email2)
        response = await auth_admin.create_user(attributes=attributes)
        assert isinstance(response, User)
        assert response.email == email2
        response = await auth_admin.list_users()
        user = next((u for u in response if u.email == email2), None)
        assert user
        assert user.email == email2
    except Exception as e:
        assert False, str(e)


def test_default_headers(client: AsyncGoTrueClient):
    """Test client for existing default headers"""
    default_key = "X-Client-Info"
    assert default_key in DEFAULT_HEADERS
    assert default_key in client.api.headers
    assert client.api.headers[default_key] == DEFAULT_HEADERS[default_key]
