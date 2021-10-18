import os
import random
import string
from typing import Any, Dict

import pytest

from gotrue.client import Client
from gotrue.lib.constants import GOTRUE_URL


def _random_string(length: int = 10) -> str:
    """Generate random string."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


def _random_phone_number() -> str:
    first = str(random.randint(100, 999))
    second = str(random.randint(1, 888)).zfill(3)
    last = str(random.randint(1, 9998)).zfill(4)
    while last in ["1111", "2222", "3333", "4444", "5555", "6666", "7777", "8888"]:
        last = str(random.randint(1, 9998)).zfill(4)
    return "{}-{}-{}".format(first, second, last)


def _assert_authenticated_user(data: Dict[str, Any]):
    """Raise assertion error if user is not logged in correctly."""
    assert "access_token" in data
    assert "refresh_token" in data
    assert data.get("status_code") == 200
    user = data.get("user")
    assert user is not None
    assert user.get("id") is not None
    assert user.get("aud") == "authenticated"


@pytest.fixture
def client():
    from gotrue import Client

    supabase_url: str = os.environ.get("SUPABASE_TEST_URL")
    supabase_key: str = os.environ.get("SUPABASE_TEST_KEY")
    if supabase_url and supabase_key:
        url: str = f"{supabase_url}/auth/v1"
        return Client(
            url=url,
            headers={"apiKey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
        )
    else:
        return Client(
            url=GOTRUE_URL,
            headers={
                "Authorization": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwicm9sZSI6InN1cGFiYXNlX2FkbWluIiwiaWF0IjoxNTE2MjM5MDIyfQ.0sOtTSTfPv5oPZxsjvBO249FI4S4p0ymHoIZ6H6z9Y8"
            },
        )


def test_user_auth_flow(client: Client):
    """Ensures user can sign up, log out and log into their account."""
    random_email: str = f"{_random_string(10)}@supamail.com"
    random_password: str = _random_string(20)
    user = client.sign_up(email=random_email, password=random_password)
    _assert_authenticated_user(user)
    assert client.current_user is not None
    assert client.current_session is not None
    # Sign user out.
    client.sign_out()
    assert client.current_user is None
    assert client.current_session is None
    user = client.sign_in(email=random_email, password=random_password)
    _assert_authenticated_user(user)
    assert client.current_user is not None
    assert client.current_session is not None


def test_get_user_and_session_methods(client: Client):
    """Ensure we can get the current user and session via the getters."""
    # Create a random user.
    random_email: str = f"{_random_string(10)}@supamail.com"
    random_password: str = _random_string(20)
    user = client.sign_up(email=random_email, password=random_password)
    _assert_authenticated_user(user)
    # Test that we get not null users and sessions.
    assert client.user() is not None
    assert client.session() is not None


def test_refresh_session(client: Client):
    """Test user can signup/in and refresh their session."""
    # Create a random user.
    random_email: str = f"{_random_string(10)}@supamail.com"
    random_password: str = _random_string(20)
    user = client.sign_up(email=random_email, password=random_password)
    _assert_authenticated_user(user)
    assert client.current_user is not None
    assert client.current_session is not None
    # Refresh users session
    data = client.refresh_session()
    assert data["status_code"] == 200
    assert client.current_user is not None
    assert client.current_session is not None


def test_send_magic_link(client: Client):
    """Tests client can send a magic link to email address."""
    random_email: str = f"{_random_string(10)}@supamail.com"
    # We send a magic link if no password is supplied with the email.
    data = client.sign_in(email=random_email)
    assert data.get("status_code") == 200


def test_set_auth(client: Client):
    """Test client can override the access_token"""
    random_email: str = f"{_random_string(10)}@supamail.com"
    random_password: str = _random_string(20)
    user = client.sign_up(email=random_email, password=random_password)
    _assert_authenticated_user(user)

    mock_access_token = _random_string(20)
    client.set_auth(mock_access_token)
    new_session = client.session()
    assert new_session["access_token"] == mock_access_token


def test_sign_up_phone_password(client: Client):
    """Test client can sign up with phone and password"""
    random_phone: str = _random_phone_number()
    random_password: str = _random_string(20)
    data = client.sign_up(phone=random_phone, password=random_password)
    _assert_authenticated_user(data)
    assert client.current_user is not None
    assert client.current_session is not None

    assert "id" in data and isinstance(data.get("id"), str)
    assert "created_at" in data and isinstance(data.get("created_at"), str)
    assert "email" in data and data.get("email") == ""
    assert "confirmation_sent_at" in data and isinstance(
        data.get("confirmation_sent_at"), str
    )
    assert "phone" in data and data.get("phone") == random_phone
    assert "aud" in data and isinstance(data.get("aud"), str)
    assert "updated_at" in data and isinstance(data.get("updated_at"), str)
    assert "app_metadata" in data and isinstance(data.get("app_metadata"), dict)
    assert (
        "provider" in data.get("app_metadata")
        and data["app_metadata"].get("provider") == "phone"
    )
    assert "user_metadata" in data and isinstance(data.get("id"), dict)
    assert (
        "status" in data.get("user_metadata")
        and data["user_metadata"].get("status") == "alpha"
    )


def test_verify_mobile_otp(client: Client):
    """Test client can verify their mobile using OTP"""
    random_token: str = "123456"
    random_phone: str = _random_phone_number()
    data = client.verify_otp(phone=random_phone, token=random_token)

    assert "session" in data and data["session"] is None
    assert "user" in data and data["user"] is None
    assert "error" in data
    assert "message" in data["error"]
    assert "Otp has expired or is invalid" in data["error"]["message"]
