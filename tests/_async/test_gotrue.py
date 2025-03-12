import unittest

from .clients import auth_client, auth_client_with_asymmetric_session
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

    assert len(spy.spy_return.get("keys")) > 0
