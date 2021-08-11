from gotrue.client import Client
import pytest
import os
from faker import Faker
from jsonschema import validate

fake = Faker()
Faker.seed(0)

GOTRUE_URL = "http://localhost:9999"
EMAIL = fake.email()
PASSWORD = fake.password()
TEST_TWILIO = False
phone = fake.phone_number()


@pytest.fixture
def client():
    from gotrue import Client

    url: str = GOTRUE_URL
    return Client(url=url, auto_refresh_token=False, persist_session=True, headers={})


@pytest.mark.asyncio
async def test_signup_with_email_and_password(client: Client):
    resp_schema = {
        "type": "object",
        "properties": {
            "aud": {"type": "string"},
            "confirmation_sent_at": {"type": "string"},
            "created_at": {"type": "string"},
            "email": {"type": "string"},
            "id": {"type": "string"},
            "phone": {"const": ""},
            "role": {"const": ""},
            "updated_at": {"type": "string"},
            "app_metadata": {"provider": {"const": "email"}},
        },
    }
    res = await client.sign_up(EMAIL, PASSWORD)
    assert res.get("status_code") == 200
    validate(res, resp_schema)


@pytest.mark.asyncio
async def test_sign_in(client: Client):
    res = await client.sign_in(EMAIL, PASSWORD)
    assert res.get("error_description") == "Email not confirmed"


@pytest.mark.asyncio
async def test_sign_in_with_wrong_password(client: Client):
    res = await client.sign_in(EMAIL, PASSWORD + "2")
    assert res.get("error_description") == "Email not confirmed"
