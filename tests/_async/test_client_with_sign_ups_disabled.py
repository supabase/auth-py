from typing import AsyncIterable

import pytest
from faker import Faker

from gotrue import AsyncGoTrueClient
from gotrue.exceptions import APIError

GOTRUE_URL = "http://localhost:9997"


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


@pytest.mark.asyncio
async def test_sign_up(client: AsyncGoTrueClient):
    expected_error_message = "Signups not allowed for this instance"
    try:
        await client.sign_up(email=email, password=password)
        assert False
    except APIError as e:
        assert e.msg == expected_error_message
    except Exception as e:
        assert False, str(e)
