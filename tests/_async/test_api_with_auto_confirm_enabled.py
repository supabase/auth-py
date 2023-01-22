from typing import AsyncIterable, Optional

import pytest
from faker import Faker

from gotrue.constants import COOKIE_OPTIONS
from gotrue.types import CookieOptions, Session, User

GOTRUE_URL = "http://localhost:9998"
TOKEN = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJyb2xlIjoic2VydmljZV9yb2xlIiwiaWF0IjoxNjQyMjMyNzUwfQ.TUR8Zu05TtNR25L42soA2trZpc4oBR8-9Pv5r5bvls8"  # noqa: E501


@pytest.fixture(name="api")
async def create_api() -> AsyncIterable[AsyncGoTrueAdminAPI]:
    async with AsyncGoTrueAdminAPI(
        url=GOTRUE_URL,
        headers={"Authorization": f"Bearer {TOKEN}"},
        cookie_options=CookieOptions.parse_obj(COOKIE_OPTIONS),
    ) as api:
        yield api


fake = Faker()

email = f"api_ac_enabled_{fake.email().lower()}"
password = fake.password()
valid_session: Optional[Session] = None


async def test_sign_up_with_email(api: AsyncGoTrueAdminAPI):
    global valid_session
    try:
        response = await api.sign_up_with_email(
            email=email,
            password=password,
            data={"status": "alpha"},
        )
        assert isinstance(response, Session)
        valid_session = response
    except Exception as e:
        assert False, str(e)


@pytest.mark.depends(on=[test_sign_up_with_email.__name__])
async def test_get_user(api: AsyncGoTrueAdminAPI):
    try:
        jwt = valid_session.access_token if valid_session else ""
        response = await api.get_user(jwt=jwt)
        assert isinstance(response, User)
    except Exception as e:
        assert False, str(e)


@pytest.mark.depends(on=[test_get_user.__name__])
async def test_delete_user(api: AsyncGoTrueAdminAPI):
    try:
        jwt = valid_session.access_token if valid_session else ""
        user = await api.get_user(jwt=jwt)
        await api.delete_user(uid=str(user.id), jwt=TOKEN)
    except Exception as e:
        assert False, str(e)
