import os
import random
import string
from typing import Any, Dict

import pytest


def _random_string(length: int = 10) -> str:
    """Generate random string."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=length))


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
    url: str = f"{supabase_url}/auth/v1"
    return Client(
        url=url,
        headers={"apiKey": supabase_key, "Authorization": f"Bearer {supabase_key}"},
    )


def test_user_auth_flow(client):
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


def test_get_user_and_session_methods(client):
    """Ensure we can get the current user and session via the getters."""
    # Create a random user.
    random_email: str = f"{_random_string(10)}@supamail.com"
    random_password: str = _random_string(20)
    user = client.sign_up(email=random_email, password=random_password)
    _assert_authenticated_user(user)
    # Test that we get not null users and sessions.
    assert client.user() is not None
    assert client.session() is not None


def test_refresh_session(client):
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


def test_send_magic_link(client):
    """Tests client can send a magic link to email address."""
    random_email: str = f"{_random_string(10)}@supamail.com"
    # We send a magic link if no password is supplied with the email.
    data = client.sign_in(email=random_email)
    assert data.get("status_code") == 200
