from typing import Iterable

import pytest
from faker import Faker

from gotrue import SyncGoTrueApi
from gotrue.constants import COOKIE_OPTIONS
from gotrue.types import CookieOptions, LinkType, User

GOTRUE_URL = "http://localhost:9999"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InN1cGFiYXNlX2FkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.0sOtTSTfPv5oPZxsjvBO249FI4S4p0ymHoIZ6H6z9Y8"  # noqa: E501


@pytest.fixture(name="api")
def create_api() -> Iterable[SyncGoTrueApi]:
    with SyncGoTrueApi(
        url=GOTRUE_URL,
        headers={"Authorization": f"Bearer {TOKEN}"},
        cookie_options=CookieOptions.from_dict(COOKIE_OPTIONS),
    ) as api:
        yield api


fake = Faker()

email = f"api_ac_disabled_{fake.email().lower()}"
password = fake.password()


@pytest.mark.asyncio
def test_sign_up_with_email_and_password(api: SyncGoTrueApi):
    try:
        response = api.sign_up_with_email(
            email=email,
            password=password,
            redirect_to="http://localhost:9999/welcome",
            data={"status": "alpha"},
        )
        assert isinstance(response, User)
    except Exception as e:
        assert False, str(e)


email2 = f"api_generate_link_signup_{fake.email().lower()}"
password2 = fake.password()


@pytest.mark.asyncio
def test_generate_sign_up_link(api: SyncGoTrueApi):
    try:
        response = api.generate_link(
            type=LinkType.signup,
            email=email2,
            password=password2,
            redirect_to="http://localhost:9999/welcome",
            data={"status": "alpha"},
        )
        assert isinstance(response, User)
    except Exception as e:
        assert False, str(e)


email3 = f"api_generate_link_signup_{fake.email().lower()}"


@pytest.mark.asyncio
def test_generate_magic_link(api: SyncGoTrueApi):
    try:
        response = api.generate_link(
            type=LinkType.magiclink,
            email=email3,
            redirect_to="http://localhost:9999/welcome",
        )
        assert isinstance(response, User)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_generate_invite_link(api: SyncGoTrueApi):
    try:
        response = api.generate_link(
            type=LinkType.invite,
            email=email3,
            redirect_to="http://localhost:9999/welcome",
        )
        assert isinstance(response, User)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up_with_email_and_password.__name__])
def test_generate_recovery_link(api: SyncGoTrueApi):
    try:
        response = api.generate_link(
            type=LinkType.recovery,
            email=email,
            redirect_to="http://localhost:9999/welcome",
        )
        assert isinstance(response, User)
    except Exception as e:
        assert False, str(e)
