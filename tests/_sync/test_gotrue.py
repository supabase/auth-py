import time
import unittest

from .clients import auth_client, auth_client_with_asymmetric_session
from .utils import mock_user_credentials


def test_get_claims_returns_none_when_session_is_none():
    claims = auth_client().get_claims()
    assert claims is None


def test_get_claims_calls_get_user_if_symmetric_jwt(mocker):
    client = auth_client()
    spy = mocker.spy(client, "get_user")

    user = (client.sign_up(mock_user_credentials())).user
    assert user is not None

    claims = (client.get_claims())["claims"]
    assert claims["email"] == user.email
    spy.assert_called_once()


def test_get_claims_fetches_jwks_to_verify_asymmetric_jwt(mocker):
    client = auth_client_with_asymmetric_session()

    user = (client.sign_up(mock_user_credentials())).user
    assert user is not None

    spy = mocker.spy(client, "_request")

    claims = (client.get_claims())["claims"]
    assert claims["email"] == user.email

    spy.assert_called_once()
    spy.assert_called_with("GET", ".well-known/jwks.json", xform=unittest.mock.ANY)

    expected_keyid = "638c54b8-28c2-4b12-9598-ba12ef610a29"

    assert len(client._jwks["keys"]) == 1
    assert client._jwks["keys"][0]["kid"] == expected_keyid


def test_jwks_ttl_cache_behavior(mocker):
    client = auth_client_with_asymmetric_session()

    spy = mocker.spy(client, "_request")

    # First call should fetch JWKS from endpoint
    user = (client.sign_up(mock_user_credentials())).user
    assert user is not None

    client.get_claims()
    spy.assert_called_with("GET", ".well-known/jwks.json", xform=unittest.mock.ANY)
    first_call_count = spy.call_count

    # Second call within TTL should use cache
    client.get_claims()
    assert spy.call_count == first_call_count  # No additional JWKS request

    # Mock time to be after TTL expiry
    original_time = time.time
    try:
        mock_time = mocker.patch("time.time")
        mock_time.return_value = original_time() + 601  # TTL is 600 seconds

        # Call after TTL expiry should fetch fresh JWKS
        client.get_claims()
        assert spy.call_count == first_call_count + 1  # One more JWKS request
    finally:
        # Restore original time function
        mocker.patch("time.time", original_time)
