import pytest
from pytest_mock import mocker

from .utils import mock_user_credentials

from .clients import auth_client

async def test_get_claims_returns_none_when_session_is_none():
  claims = await auth_client().get_claims()
  assert claims is None

async def test_get_claims_calls_get_user_if_symmetric_jwt(mocker):
  client = auth_client()
  credentials = mock_user_credentials()
  spy = mocker.spy(client, 'get_user')

  response = await client.sign_up(credentials)
  user = response.user
  assert user is not None

  response = await client.get_claims()
  assert response["claims"]["email"] == user.email
  spy.assert_called_once()
  