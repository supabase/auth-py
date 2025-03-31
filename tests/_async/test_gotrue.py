import time
import unittest

import pytest
from jwt import encode

from supabase_auth.errors import AuthInvalidJwtError, AuthSessionMissingError
from supabase_auth.helpers import decode_jwt

from .clients import (
    GOTRUE_JWT_SECRET,
    auth_client,
    auth_client_with_asymmetric_session,
    auth_client_with_session,
)
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


async def test_mfa_enroll():
    client = auth_client_with_session()

    credentials = mock_user_credentials()

    # First sign up to get a valid session
    await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )

    # Test MFA enrollment
    enroll_response = await client.mfa.enroll(
        {"issuer": "test-issuer", "factor_type": "totp", "friendly_name": "test-factor"}
    )

    assert enroll_response.id is not None
    assert enroll_response.type == "totp"
    assert enroll_response.friendly_name == "test-factor"
    assert enroll_response.totp.qr_code is not None


async def test_mfa_challenge():
    client = auth_client()
    credentials = mock_user_credentials()

    # First sign up to get a valid session
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None

    # Enroll a factor first
    enroll_response = await client.mfa.enroll(
        {"factor_type": "totp", "issuer": "test-issuer", "friendly_name": "test-factor"}
    )

    # Test MFA challenge
    challenge_response = await client.mfa.challenge({"factor_id": enroll_response.id})
    assert challenge_response.id is not None
    assert challenge_response.expires_at is not None


async def test_mfa_unenroll():
    client = auth_client()
    credentials = mock_user_credentials()

    # First sign up to get a valid session
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None

    # Enroll a factor first
    enroll_response = await client.mfa.enroll(
        {"factor_type": "totp", "issuer": "test-issuer", "friendly_name": "test-factor"}
    )

    # Test MFA unenroll
    unenroll_response = await client.mfa.unenroll({"factor_id": enroll_response.id})
    assert unenroll_response.id == enroll_response.id


async def test_mfa_list_factors():
    client = auth_client()
    credentials = mock_user_credentials()

    # First sign up to get a valid session
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None

    # Enroll a factor first
    await client.mfa.enroll(
        {"factor_type": "totp", "issuer": "test-issuer", "friendly_name": "test-factor"}
    )

    # Test MFA list factors
    list_response = await client.mfa.list_factors()
    assert len(list_response.all) == 1


async def test_initialize_from_url():
    client = auth_client()
    credentials = mock_user_credentials()
    
    # Sign up to get a valid session
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None
    
    # Create a mock URL with access_token and refresh_token as query parameters
    mock_url = f"http://example.com/?access_token={signup_response.session.access_token}&refresh_token={signup_response.session.refresh_token}&expires_in=3600&token_type=bearer"
    
    # Clear the session
    await client._remove_session()
    
    # Need to mock _get_session_from_url to return a valid session
    from unittest.mock import patch
    from supabase_auth.types import Session
    
    # Create a reference to the original session
    original_session = signup_response.session
    
    # Mock the _get_session_from_url method to return the original session
    with patch.object(client, '_get_session_from_url', return_value=(original_session, "signup")) as mock_method:
        # Test initialize_from_url
        await client.initialize_from_url(mock_url)
        
        # Verify _get_session_from_url was called with the right URL
        mock_method.assert_called_once_with(mock_url)
    
    # Verify the session was restored
    session = await client.get_session()
    assert session is not None
    assert session.access_token == signup_response.session.access_token


async def test_exchange_code_for_session(mocker):
    client = auth_client()
    
    # Create a proper AuthResponse-like object
    from supabase_auth.types import Session, User, AuthResponse
    
    mock_user = User(
        id="mock_user_id",
        email="mock@example.com",
        app_metadata={},
        user_metadata={},
        created_at="2023-01-01T00:00:00Z",  # Valid ISO timestamp
        aud="",
    )
    
    mock_session = Session(
        access_token="mock_access_token",
        refresh_token="mock_refresh_token",
        expires_in=3600,
        expires_at=int(time.time()) + 3600,
        token_type="bearer",
        user=mock_user
    )
    
    mock_auth_response = AuthResponse(
        session=mock_session,
        user=mock_user
    )
    
    # Mock the _request method to return a valid auth response
    mocker.patch.object(
        client, 
        '_request', 
        return_value=mock_auth_response
    )
    
    # Mock storage.get_item to return a code verifier
    mocker.patch.object(
        client._storage,
        'get_item',
        return_value="mock_code_verifier"
    )
    
    # Also mock the _save_session method to prevent actual saving
    mocker.patch.object(client, '_save_session')
    
    # Also mock the _notify_all_subscribers method
    mocker.patch.object(client, '_notify_all_subscribers')
    
    # Mock the storage.remove_item method
    mocker.patch.object(client._storage, 'remove_item')
    
    # Test exchange_code_for_session
    response = await client.exchange_code_for_session({
        "auth_code": "mock_auth_code"
    })
    
    # Verify response has a session
    assert response.session is not None
    assert response.session.access_token == "mock_access_token"
    
    # Verify _request was called with the right parameters
    client._request.assert_called_once_with(
        "POST",
        "token",
        query={"grant_type": "pkce"},
        body={
            "auth_code": "mock_auth_code",
            "code_verifier": "mock_code_verifier",
        },
        redirect_to=None,
        xform=mocker.ANY
    )


async def test_get_authenticator_assurance_level():
    client = auth_client()
    credentials = mock_user_credentials()
    
    # Test without session
    response = await client.mfa.get_authenticator_assurance_level()
    assert response.current_level is None
    assert response.next_level is None
    assert response.current_authentication_methods == []
    
    # Sign up to get a valid session
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None
    
    # Test with session
    response = await client.mfa.get_authenticator_assurance_level()
    assert response.current_authentication_methods is not None


