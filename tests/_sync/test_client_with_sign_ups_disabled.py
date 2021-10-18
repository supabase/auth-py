import pytest
from faker import Faker

from gotrue import SyncGoTrueClient
from gotrue.types import ApiError

GOTRUE_URL = "http://localhost:9997"


def create_client() -> SyncGoTrueClient:
    return SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    )


fake = Faker()

email = fake.email().lower()
password = fake.password()


@pytest.mark.asyncio
def test_sign_up():
    expected_error_message = "Signups not allowed for this instance"
    try:
        print(email, password)
        with create_client() as client:
            client.sign_up(email=email, password=password)
    except ApiError as e:
        assert e.msg == expected_error_message
    except Exception as e:
        assert False, str(e)
