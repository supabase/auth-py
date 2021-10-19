from typing import Optional

import pytest
from faker import Faker

from gotrue import SyncGoTrueClient
from gotrue.types import ApiError, Session, User, UserAttributes

GOTRUE_URL = "http://localhost:9998"
TEST_TWILIO = False


@pytest.fixture(name="client")
def create_client() -> SyncGoTrueClient:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=True,
    ) as client:
        yield client


@pytest.fixture(name="client_with_session")
def create_client_with_session() -> SyncGoTrueClient:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


@pytest.fixture(name="new_client")
def create_new_client() -> SyncGoTrueClient:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


fake = Faker()

email = f"client_ac_enabled_{fake.email().lower()}"
set_session_email = f"client_ac_session_{fake.email().lower()}"
refresh_token_email = f"client_refresh_token_signin_{fake.email().lower()}"
password = fake.password()
access_token: Optional[str] = None


@pytest.mark.asyncio
def test_sign_up(client: SyncGoTrueClient):
    try:
        response = client.sign_up(
            email=email,
            password=password,
            data={"status": "alpha"},
        )
        assert isinstance(response, Session)
        global access_token
        access_token = response.access_token
        assert response.access_token
        assert response.refresh_token
        assert response.expires_in
        assert response.expires_at
        assert response.user
        assert response.user.id
        assert response.user.email == email
        assert response.user.email_confirmed_at
        assert response.user.last_sign_in_at
        assert response.user.created_at
        assert response.user.updated_at
        assert response.user.app_metadata
        assert response.user.app_metadata.get("provider") == "email"
        assert response.user.user_metadata
        assert response.user.user_metadata.get("status") == "alpha"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_set_session_should_return_no_error(
    client_with_session: SyncGoTrueClient,
):
    try:
        response = client_with_session.sign_up(
            email=set_session_email,
            password=password,
        )
        assert isinstance(response, Session)
        assert response.refresh_token
        client_with_session.set_session(refresh_token=response.refresh_token)
        data = {"hello": "world"}
        response = client_with_session.update(attributes=UserAttributes(data=data))
        assert response.user_metadata == data
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_sign_up_the_same_user_twice_should_throw_an_error(
    client: SyncGoTrueClient,
):
    expected_error_message = (
        "Thanks for registering, now check your email to complete the process."
    )
    try:
        client.sign_up(email=email, password=password)
        assert False
    except ApiError as e:
        assert e.msg == expected_error_message
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_set_auth_should_set_the_auth_headers_on_a_new_client(
    new_client: SyncGoTrueClient,
):
    try:
        assert access_token
        new_client.set_auth(access_token=access_token)
        assert new_client.current_session
        assert new_client.current_session.access_token == access_token
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_sign_in(client: SyncGoTrueClient):
    try:
        response = client.sign_in(email=email, password=password)
        assert isinstance(response, Session)
        assert response.access_token
        assert response.refresh_token
        assert response.expires_in
        assert response.expires_at
        assert response.user
        assert response.user.id
        assert response.user.email == email
        assert response.user.email_confirmed_at
        assert response.user.last_sign_in_at
        assert response.user.created_at
        assert response.user.updated_at
        assert response.user.app_metadata
        assert response.user.app_metadata.get("provider") == "email"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_refresh_token(client_with_session: SyncGoTrueClient):
    try:
        response = client_with_session.sign_up(
            email=refresh_token_email,
            password=password,
        )
        assert isinstance(response, Session)
        assert response.refresh_token
        response2 = client_with_session.sign_in(refresh_token=response.refresh_token)
        assert isinstance(response2, Session)
        assert response2.access_token
        assert response2.refresh_token
        assert response2.expires_in
        assert response2.expires_at
        assert response2.user
        assert response2.user.id
        assert response2.user.email == refresh_token_email
        assert response2.user.email_confirmed_at
        assert response2.user.last_sign_in_at
        assert response2.user.created_at
        assert response2.user.updated_at
        assert response2.user.app_metadata
        assert response2.user.app_metadata.get("provider") == "email"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_in.__name__])
def test_get_user(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.user()
        assert isinstance(response, User)
        assert response.id
        assert response.email == email
        assert response.email_confirmed_at
        assert response.last_sign_in_at
        assert response.created_at
        assert response.updated_at
        assert response.app_metadata
        provider = response.app_metadata.get("provider")
        assert provider == "email"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_in.__name__])
def test_update_user(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.update(attributes=UserAttributes(data={"hello": "world"}))
        assert isinstance(response, User)
        assert response.id
        assert response.email == email
        assert response.email_confirmed_at
        assert response.last_sign_in_at
        assert response.created_at
        assert response.updated_at
        assert response.user_metadata
        assert response.user_metadata.get("hello") == "world"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_update_user.__name__])
def test_get_user_after_update(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.user()
        assert isinstance(response, User)
        assert response.id
        assert response.email == email
        assert response.email_confirmed_at
        assert response.last_sign_in_at
        assert response.created_at
        assert response.updated_at
        assert response.user_metadata
        assert response.user_metadata.get("hello") == "world"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_get_user_after_update.__name__])
def test_sign_out(client: SyncGoTrueClient):
    try:
        client.sign_out()
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_out.__name__])
def test_get_user_after_sign_out(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.user()
        assert not response
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_get_user_after_sign_out.__name__])
def test_sign_in_with_the_wrong_password(client: SyncGoTrueClient):
    try:
        client.sign_in(email=email, password=password + "2")
        assert False
    except ApiError:
        assert True
    except Exception as e:
        assert False, str(e)


# @pytest.mark.asyncio
# @pytest.mark.depends(on=[test_sign_up_with_email_and_password.__name__])
# async def test_sign_up_with_the_same_user_twice_should_throw_an_error(
#     client: AsyncGoTrueClient,
# ):
#     expected_error_message = "For security purposes, you can only request this after"
#     try:
#         await client.sign_up(
#             email=email,
#             password=password,
#         )
#         assert False
#     except ApiError as e:
#         assert expected_error_message in e.msg
#     except Exception as e:
#         assert False, str(e)


# @pytest.mark.asyncio
# @pytest.mark.depends(on=[test_sign_up_with_email_and_password.__name__])
# async def test_sign_in(client: AsyncGoTrueClient):
#     expected_error_message = "Email not confirmed"
#     try:
#         await client.sign_in(
#             email=email,
#             password=password,
#         )
#         assert False
#     except ApiError as e:
#         assert e.msg == expected_error_message
#     except Exception as e:
#         assert False, str(e)


# @pytest.mark.asyncio
# @pytest.mark.depends(on=[test_sign_up_with_email_and_password.__name__])
# async def test_sign_in_with_the_wrong_password(client: AsyncGoTrueClient):
#     expected_error_message = "Email not confirmed"
#     try:
#         await client.sign_in(
#             email=email,
#             password=password + "2",
#         )
#         assert False
#     except ApiError as e:
#         assert e.msg == expected_error_message
#     except Exception as e:
#         assert False, str(e)


# @pytest.mark.asyncio
# @pytest.mark.skipif(not TEST_TWILIO, reason="Twilio is not available")
# async def test_sign_up_with_phone_and_password(client: AsyncGoTrueClient):
#     try:
#         response = await client.sign_up(
#             phone=phone,
#             password=password,
#             data={"status": "alpha"},
#         )
#         assert isinstance(response, User)
#         assert not response.phone_confirmed_at
#         assert not response.email_confirmed_at
#         assert not response.last_sign_in_at
#         assert response.phone == phone
#     except Exception as e:
#         assert False, str(e)


# @pytest.mark.asyncio
# @pytest.mark.skipif(not TEST_TWILIO, reason="Twilio is not available")
# @pytest.mark.depends(on=[test_sign_up_with_phone_and_password.__name__])
# async def test_verify_mobile_otp_errors_on_bad_token(client: AsyncGoTrueClient):
#     expected_error_message = "Otp has expired or is invalid"
#     try:
#         await client.verify_otp(phone=phone, token="123456")
#         assert False
#     except ApiError as e:
#         assert expected_error_message in e.msg
#     except Exception as e:
#         assert False, str(e)
