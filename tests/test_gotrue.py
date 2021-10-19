# import os
# import random
# import string
# from typing import Optional

# import pytest
# from gotrue import AsyncGoTrueClient
# from gotrue.constants import GOTRUE_URL
# from gotrue.types import ApiError, Session


# def _random_string(length: int = 10) -> str:
#     """Generate random string."""
#     return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


# def _random_phone_number() -> str:
#     first = str(random.randint(100, 999))
#     second = str(random.randint(1, 888)).zfill(3)
#     last = str(random.randint(1, 9998)).zfill(4)
#     while last in ["1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888"]:
#         last = str(random.randint(1, 9998)).zfill(4)
#     return "{}-{}-{}".format(first, second, last)


# def _assert_authenticated_user(data: Session):
#     """Raise assertion error if user is not logged in correctly."""
#     assert data.access_token
#     assert data.refresh_token
#     assert data.user
#     assert data.user.id
#     assert data.user.aud == "authenticated"


# @pytest.fixture
# def client():
#     from gotrue import AsyncGoTrueClient

#     supabase_url = os.environ.get("SUPABASE_TEST_URL")
#     supabase_key = os.environ.get("SUPABASE_TEST_KEY")
#     if supabase_url and supabase_key:
#         url: str = f"{supabase_url}/auth/v1"
#         return AsyncGoTrueClient(
#             url=url,
#             headers={"apiKey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
#         )
#     else:
#         return AsyncGoTrueClient(
#             url=GOTRUE_URL,
#             headers={
#                 "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InN1cGFiYXNlX2FkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.0sOtTSTfPv5oPZxsjvBO249FI4S4p0ymHoIZ6H6z9Y8"
#             },
#         )


# @pytest.mark.asyncio
# async def test_user_auth_flow(client: AsyncGoTrueClient):
#     """Ensures user can sign up, log out and log into their account."""
#     random_email = f"{_random_string(10)}@supamail.com"
#     random_password = _random_string(20)
#     response = await client.sign_up(email=random_email, password=random_password)
#     assert isinstance(response, Session)
#     _assert_authenticated_user(response)
#     assert client.current_user
#     assert client.current_session
#     # Sign user out.
#     await client.sign_out()
#     assert not client.current_user
#     assert not client.current_session
#     response = await client.sign_in(email=random_email, password=random_password)
#     assert isinstance(response, Session)
#     _assert_authenticated_user(response)
#     assert client.current_user
#     assert client.current_session


# @pytest.mark.asyncio
# async def test_get_user_and_session_methods(client: AsyncGoTrueClient):
#     """Ensure we can get the current user and session via the getters."""
#     # Create a random user.
#     random_email = f"{_random_string(10)}@supamail.com"
#     random_password = _random_string(20)
#     response = await client.sign_up(email=random_email, password=random_password)
#     assert isinstance(response, Session)
#     _assert_authenticated_user(response)
#     # Test that we get not null users and sessions.
#     assert client.user()
#     assert client.session()


# @pytest.mark.asyncio
# async def test_refresh_session(client: AsyncGoTrueClient):
#     """Test user can signup/in and refresh their session."""
#     # Create a random user.
#     random_email = f"{_random_string(10)}@supamail.com"
#     random_password = _random_string(20)
#     response = await client.sign_up(email=random_email, password=random_password)
#     assert isinstance(response, Session)
#     _assert_authenticated_user(response)
#     assert client.current_user
#     assert client.current_session
#     # Refresh users session
#     response = await client.refresh_session()
#     assert client.current_user
#     assert client.current_session


# @pytest.mark.asyncio
# async def test_send_magic_link(client: AsyncGoTrueClient):
#     """Tests client can send a magic link to email address."""
#     random_email = f"{_random_string(10)}@supamail.com"
#     # We send a magic link if no password is supplied with the email.
#     await client.sign_in(email=random_email)


# @pytest.mark.asyncio
# async def test_set_auth(client: AsyncGoTrueClient):
#     """Test client can override the access_token"""
#     random_email = f"{_random_string(10)}@supamail.com"
#     random_password = _random_string(20)
#     response = await client.sign_up(email=random_email, password=random_password)
#     assert isinstance(response, Session)
#     _assert_authenticated_user(response)
#     mock_access_token = _random_string(20)
#     await client.set_auth(access_token=mock_access_token)
#     new_session = client.session()
#     assert new_session
#     assert new_session.access_token == mock_access_token


# @pytest.mark.asyncio
# async def test_sign_up_phone_password(client: AsyncGoTrueClient):
#     """Test client can sign up with phone and password"""
#     random_phone = _random_phone_number()
#     random_password = _random_string(20)
#     response = client.sign_up(phone=random_phone, password=random_password)
#     assert isinstance(response, Session)
#     _assert_authenticated_user(response)
#     assert client.current_user
#     assert client.current_session
#     assert "id" in response and isinstance(response.get("id"), str)
#     assert "created_at" in response and isinstance(response.get("created_at"), str)
#     assert "email" in response and response.get("email") == ""
#     assert "confirmation_sent_at" in response and isinstance(
#         response.get("confirmation_sent_at"), str
#     )
#     assert "phone" in response and response.get("phone") == random_phone
#     assert "aud" in response and isinstance(response.get("aud"), str)
#     assert "updated_at" in response and isinstance(response.get("updated_at"), str)
#     assert "app_metadata" in response and isinstance(response.get("app_metadata"), dict)
#     assert (
#         "provider" in response.get("app_metadata")
#         and response["app_metadata"].get("provider") == "phone"
#     )
#     assert "user_metadata" in response and isinstance(response.get("id"), dict)
#     assert (
#         "status" in response.get("user_metadata")
#         and response["user_metadata"].get("status") == "alpha"
#     )


# @pytest.mark.asyncio
# async def test_verify_mobile_otp(client: AsyncGoTrueClient):
#     """Test client can verify their mobile using OTP"""
#     random_token = "123456"
#     random_phone = _random_phone_number()
#     try:
#         await client.verify_otp(phone=random_phone, token=random_token)
#     except ApiError as e:
#         assert "Otp has expired or is invalid" in e.msg
