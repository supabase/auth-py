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
    # This test verifies the URL format detection and initialization from URL
    client = auth_client()
    
    # First we'll test the _is_implicit_grant_flow method
    # The method checks for access_token or error_description in the query string, not the fragment
    url_with_token = "http://example.com/?access_token=test_token&other=value"
    assert client._is_implicit_grant_flow(url_with_token) == True
    
    url_with_error = "http://example.com/?error_description=test_error&other=value"
    assert client._is_implicit_grant_flow(url_with_error) == True
    
    url_without_token = "http://example.com/?other=value"
    assert client._is_implicit_grant_flow(url_without_token) == False
    
    # Now we'll test the initialize method with mocks
    from unittest.mock import patch
    
    # Create a URL that will pass the _is_implicit_grant_flow check
    good_url = "http://example.com/?access_token=test_token&refresh_token=test_refresh&expires_in=3600&token_type=bearer"
    
    # Test initialize method with a valid URL
    with patch.object(client, 'initialize_from_url') as mock_init_url:
        await client.initialize(url=good_url)
        mock_init_url.assert_called_once_with(good_url)
    
    # Test initialize method with an invalid URL
    with patch.object(client, 'initialize_from_storage') as mock_init_storage:
        await client.initialize(url="http://example.com/no_token_here")
        mock_init_storage.assert_called_once()


async def test_exchange_code_for_session():
    client = auth_client()
    
    # We'll test the flow type setting instead of the actual exchange, since the
    # actual exchange requires a live OAuth flow which isn't practical in tests
    assert client._flow_type in ["implicit", "pkce"]
    
    # This part would normally need a live OAuth flow, so we verify the logic paths
    # Get the storage key for PKCE flow
    storage_key = f"{client._storage_key}-code-verifier"
    
    # Set the flow type to pkce
    client._flow_type = "pkce"
    
    # Test the PKCE URL generation which is needed for exchange_code_for_session
    provider = "github"
    url, params = await client._get_url_for_provider(
        f"{client._url}/authorize", provider, {}
    )
    
    # Verify PKCE parameters were added
    assert "code_challenge" in params
    assert "code_challenge_method" in params
    
    # Verify the code verifier was stored
    code_verifier = await client._storage.get_item(storage_key)
    assert code_verifier is not None


async def test_get_authenticator_assurance_level():
    client = auth_client()
    credentials = mock_user_credentials()
    
    # Without a session, should return null values
    aal_response = await client.mfa.get_authenticator_assurance_level()
    assert aal_response.current_level is None
    assert aal_response.next_level is None
    assert aal_response.current_authentication_methods == []
    
    # Sign up to get a valid session
    signup_response = await client.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert signup_response.session is not None
    
    # With a session, should return authentication methods
    aal_response = await client.mfa.get_authenticator_assurance_level()
    # Basic auth will have password as an authentication method
    assert aal_response.current_authentication_methods is not None


async def test_link_identity():
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
    
    from unittest.mock import patch
    from supabase_auth.types import OAuthResponse
    
    # Since the test server has manual linking disabled, we'll mock the URL generation
    with patch.object(client, '_get_url_for_provider') as mock_url_provider:
        mock_url = "http://example.com/authorize?provider=github"
        mock_params = {"provider": "github"}
        mock_url_provider.return_value = (mock_url, mock_params)
        
        # Also mock the _request method since the server would reject it
        with patch.object(client, '_request') as mock_request:
            mock_request.return_value = OAuthResponse(provider="github", url=mock_url)
            
            # Call the method
            response = await client.link_identity({"provider": "github"})
            
            # Verify the response
            assert response.provider == "github"
            assert response.url == mock_url


async def test_get_user_identities():
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
    
    # New users won't have any identities yet, but the call should work
    identities_response = await client.get_user_identities()
    assert identities_response is not None
    # For a new user, identities will be an empty list or None
    assert hasattr(identities_response, "identities")


async def test_sign_in_with_sso():
    client = auth_client()
    
    # Test sign in with domain
    from unittest.mock import patch
    from supabase_auth.types import SSOResponse
    from supabase_auth.errors import AuthInvalidCredentialsError
    
    with patch.object(client, '_request') as mock_request:
        mock_response = SSOResponse(url="https://example.com/sso/redirect")
        mock_request.return_value = mock_response
        
        # Call sign_in_with_sso with domain
        response = await client.sign_in_with_sso({
            "domain": "example.com",
            "options": {
                "redirect_to": "https://example.com/callback",
                "skip_http_redirect": True,
            },
        })
        
        # Verify the response
        assert response.url == "https://example.com/sso/redirect"
        
        # Verify the request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == "POST"
        assert args[1] == "sso"
        assert "domain" in kwargs.get("body", {})
        assert kwargs.get("body", {}).get("domain") == "example.com"
        
    # Test sign in with provider_id
    with patch.object(client, '_request') as mock_request:
        mock_response = SSOResponse(url="https://example.com/sso/redirect")
        mock_request.return_value = mock_response
        
        # Call sign_in_with_sso with provider_id
        response = await client.sign_in_with_sso({
            "provider_id": "provider123",
            "options": {
                "redirect_to": "https://example.com/callback",
                "skip_http_redirect": True,
            },
        })
        
        # Verify the response
        assert response.url == "https://example.com/sso/redirect"
        
        # Verify the request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert "provider_id" in kwargs.get("body", {})
        assert kwargs.get("body", {}).get("provider_id") == "provider123"
    
    # Test invalid parameters
    with pytest.raises(AuthInvalidCredentialsError):
        await client.sign_in_with_sso({})


async def test_sign_in_with_id_token():
    client = auth_client()
    
    # Create mocked response
    from unittest.mock import patch
    
    # Use patch for _request to avoid actual API calls
    with patch.object(client, '_request') as mock_request:
        from supabase_auth.types import AuthResponse, Session, User
        
        mock_user = User(
            id="mock_user_id",
            email="mock@example.com",
            app_metadata={},
            user_metadata={},
            created_at="2023-01-01T00:00:00Z",
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
        
        mock_request.return_value = mock_auth_response
        
        # Call sign_in_with_id_token
        credentials = {
            "provider": "google",
            "token": "mock_id_token",
            "access_token": "mock_access_token",
            "nonce": "mock_nonce",
            "options": {
                "captcha_token": "mock_captcha_token"
            }
        }
        
        response = await client.sign_in_with_id_token(credentials)
        
        # Verify response
        assert response.session == mock_session
        assert response.user == mock_user
        
        # Verify the request was made with correct parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        
        assert args[0] == "POST"
        assert args[1] == "token"
        assert kwargs.get("query", {}).get("grant_type") == "id_token"
        assert kwargs.get("body", {}).get("provider") == "google"
        assert kwargs.get("body", {}).get("id_token") == "mock_id_token"
        assert kwargs.get("body", {}).get("access_token") == "mock_access_token"
        assert kwargs.get("body", {}).get("nonce") == "mock_nonce"
        assert kwargs.get("body", {}).get("gotrue_meta_security", {}).get("captcha_token") == "mock_captcha_token"


async def test_sign_in_with_oauth():
    client = auth_client()
    
    # Test with various providers
    for provider in ["google", "github", "facebook"]:
        # Test with minimal options
        credentials = {
            "provider": provider,
        }
        
        response = await client.sign_in_with_oauth(credentials)
        
        # Verify response structure 
        assert response.provider == provider
        assert response.url is not None
        assert provider in response.url
        
        # Test with additional options
        credentials = {
            "provider": provider,
            "options": {
                "redirect_to": "https://example.com/callback",
                "scopes": "email,profile",
                "query_params": {
                    "access_type": "offline",
                    "prompt": "consent"
                }
            }
        }
        
        response = await client.sign_in_with_oauth(credentials)
        
        # Verify response contains the redirect_to and scopes in URL
        assert "redirect_to=https%3A%2F%2Fexample.com%2Fcallback" in response.url
        assert "scopes=email%2Cprofile" in response.url


async def test_reauthenticate():
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
    
    # Test reauthenticate with a valid session
    from unittest.mock import patch
    
    with patch.object(client, '_request') as mock_request:
        # Create a mock response
        from supabase_auth.types import AuthResponse, Session, User
        
        # Use the real user from the signed-up session
        session = signup_response.session
        user = session.user
        
        mock_auth_response = AuthResponse(
            session=session,
            user=user
        )
        
        mock_request.return_value = mock_auth_response
        
        # Call reauthenticate
        response = await client.reauthenticate()
        
        # Verify the response
        assert response.session == session
        assert response.user == user
        
        # Verify the request parameters
        mock_request.assert_called_once()
        args, kwargs = mock_request.call_args
        assert args[0] == "GET"
        assert args[1] == "reauthenticate"
        assert kwargs.get("jwt") == session.access_token
    
    # Test error when no session is available
    from supabase_auth.errors import AuthSessionMissingError
    
    # Create a new client with no session
    new_client = auth_client()
    
    # Try to reauthenticate without a session
    with pytest.raises(AuthSessionMissingError):
        await new_client.reauthenticate()


async def test_sign_out():
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
    session = signup_response.session
    
    # Track sign-out events with a mock callback
    from unittest.mock import MagicMock, patch
    auth_callback = MagicMock()
    client.on_auth_state_change(auth_callback)
    
    # Test sign_out with different scopes
    for scope in ["global", "local", "others"]:
        auth_callback.reset_mock()  # Clear previous calls
        
        # Mock the admin.sign_out to avoid actual API calls
        with patch.object(client.admin, 'sign_out') as mock_admin_sign_out:
            # Reset session for each test
            await client.set_session(session.access_token, session.refresh_token)
            assert await client.get_session() is not None
            
            # Clear callback history after setting session (which triggers TOKEN_REFRESHED)
            auth_callback.reset_mock()

            # Call sign_out
            await client.sign_out({"scope": scope})
            
            # Verify admin.sign_out was called if scope is not "local"
            if scope != "local":
                mock_admin_sign_out.assert_called_once_with(session.access_token, scope)
            
            # Verify session was removed if scope is not "others"
            if scope != "others":
                assert await client.get_session() is None
                # Verify subscribers were notified with SIGNED_OUT
                auth_callback.assert_called_with("SIGNED_OUT", None)
            else:
                # For "others" scope, session should remain
                assert await client.get_session() is not None
    
    # Test unsubscribe
    unsubscribe_callback = MagicMock()
    subscription = client.on_auth_state_change(unsubscribe_callback)
    subscription.unsubscribe()

    # Session should be None at this point due to previous sign_out
    await client.sign_out()
    unsubscribe_callback.assert_not_called()  # Shouldn't be called after unsubscribing

