import time
import unittest

import pytest
from jwt import encode

from supabase_auth.errors import AuthInvalidJwtError, AuthSessionMissingError
from supabase_auth.helpers import decode_jwt

from .clients import GOTRUE_JWT_SECRET, auth_client, auth_client_with_asymmetric_session
from .utils import mock_user_credentials


async def test_get_claims_returns_none_when_session_is_none():
    claims = await auth_client().get_claims()
    assert claims is None


async def test_get_claims_calls_get_user_if_symmetric_jwt(mocker):
    client = auth_client()
    spy = mocker.spy(client, "get_user")

    user = (await client.sign_up(mock_user_credentials())).user
    assert user is not None

    claims = (await client.get_claims())["claims"]
    assert claims["email"] == user.email
    spy.assert_called_once()


async def test_get_claims_fetches_jwks_to_verify_asymmetric_jwt(mocker):
    client = auth_client_with_asymmetric_session()

    user = (await client.sign_up(mock_user_credentials())).user
    assert user is not None

    spy = mocker.spy(client, "_request")

    claims = (await client.get_claims())["claims"]
    assert claims["email"] == user.email

    spy.assert_called_once()
    spy.assert_called_with("GET", ".well-known/jwks.json", xform=unittest.mock.ANY)

    expected_keyid = "638c54b8-28c2-4b12-9598-ba12ef610a29"

    assert len(client._jwks["keys"]) == 1
    assert client._jwks["keys"][0]["kid"] == expected_keyid


async def test_jwks_ttl_cache_behavior(mocker):
    client = auth_client_with_asymmetric_session()

    spy = mocker.spy(client, "_request")

    # First call should fetch JWKS from endpoint
    user = (await client.sign_up(mock_user_credentials())).user
    assert user is not None

    await client.get_claims()
    spy.assert_called_with("GET", ".well-known/jwks.json", xform=unittest.mock.ANY)
    first_call_count = spy.call_count

    # Second call within TTL should use cache
    await client.get_claims()
    assert spy.call_count == first_call_count  # No additional JWKS request

    # Mock time to be after TTL expiry
    original_time = time.time
    try:
        mock_time = mocker.patch("time.time")
        mock_time.return_value = original_time() + 601  # TTL is 600 seconds

        # Call after TTL expiry should fetch fresh JWKS
        await client.get_claims()
        assert spy.call_count == first_call_count + 1  # One more JWKS request
    finally:
        # Restore original time function
        mocker.patch("time.time", original_time)


async def test_set_session_with_valid_tokens():
    client = auth_client()
    credentials = mock_user_credentials()

    # First sign up to get valid tokens
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None

    # Get the tokens from the signup response
    access_token = signup_response.session.access_token
    refresh_token = signup_response.session.refresh_token

    # Clear the session
    await client._remove_session()

    # Set the session with the tokens
    response = await client.set_session(access_token, refresh_token)

    # Verify the response
    assert response.session is not None
    assert response.session.access_token == access_token
    assert response.session.refresh_token == refresh_token
    assert response.user is not None
    assert response.user.email == credentials.get("email")


async def test_set_session_with_expired_token():
    client = auth_client()
    credentials = mock_user_credentials()

    # First sign up to get valid tokens
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None

    # Get the tokens from the signup response
    access_token = signup_response.session.access_token
    refresh_token = signup_response.session.refresh_token

    # Clear the session
    await client._remove_session()

    # Create an expired token by modifying the JWT
    expired_token = access_token.split(".")
    payload = decode_jwt(access_token)["payload"]
    payload["exp"] = int(time.time()) - 3600  # Set expiry to 1 hour ago
    expired_token[1] = encode(payload, GOTRUE_JWT_SECRET, algorithm="HS256").split(".")[
        1
    ]
    expired_access_token = ".".join(expired_token)

    # Set the session with the expired token
    response = await client.set_session(expired_access_token, refresh_token)

    # Verify the response has a new access token (refreshed)
    assert response.session is not None
    assert response.session.access_token != expired_access_token
    assert response.session.refresh_token != refresh_token
    assert response.user is not None
    assert response.user.email == credentials.get("email")


async def test_set_session_without_refresh_token():
    client = auth_client()
    credentials = mock_user_credentials()

    # First sign up to get valid tokens
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None

    # Get the access token from the signup response
    access_token = signup_response.session.access_token

    # Clear the session
    await client._remove_session()

    # Create an expired token
    expired_token = access_token.split(".")
    payload = decode_jwt(access_token)["payload"]
    payload["exp"] = int(time.time()) - 3600  # Set expiry to 1 hour ago
    expired_token[1] = encode(payload, GOTRUE_JWT_SECRET, algorithm="HS256").split(".")[
        1
    ]
    expired_access_token = ".".join(expired_token)

    # Try to set the session with an expired token but no refresh token
    with pytest.raises(AuthSessionMissingError):
        await client.set_session(expired_access_token, "")


async def test_set_session_with_invalid_token():
    client = auth_client()

    # Try to set the session with invalid tokens
    with pytest.raises(AuthInvalidJwtError):
        await client.set_session("invalid.token.here", "invalid_refresh_token")
