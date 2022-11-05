from .clients import auth_client_with_session, service_role_api_client
from .utils import (
    create_new_user_with_email,
    mock_app_metadata,
    mock_user_credentials,
    mock_user_metadata,
)


async def test_create_user_should_create_a_new_user():
    credentials = mock_user_credentials()
    response = await create_new_user_with_email(email=credentials.get("email"))
    assert response.email == credentials.get("email")


async def test_create_user_with_user_metadata():
    user_metadata = mock_user_metadata()
    credentials = mock_user_credentials()
    response = await service_role_api_client().create_user(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
            "user_metadata": user_metadata,
        }
    )
    assert response.user.email == credentials.get("email")
    assert response.user.user_metadata == user_metadata
    assert "profile_image" in response.user.user_metadata


async def test_create_user_with_app_metadata():
    app_metadata = mock_app_metadata()
    credentials = mock_user_credentials()
    response = await service_role_api_client().create_user(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
            "app_metadata": app_metadata,
        }
    )
    assert response.user.email == credentials.get("email")
    assert "provider" in response.user.app_metadata
    assert "providers" in response.user.app_metadata


async def test_create_user_with_user_and_app_metadata():
    user_metadata = mock_user_metadata()
    app_metadata = mock_app_metadata()
    credentials = mock_user_credentials()
    response = await service_role_api_client().create_user(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
            "user_metadata": user_metadata,
            "app_metadata": app_metadata,
        }
    )
    assert response.user.email == credentials.get("email")
    assert "profile_image" in response.user.user_metadata
    assert "provider" in response.user.app_metadata
    assert "providers" in response.user.app_metadata


async def test_list_users_should_return_registered_users():
    credentials = mock_user_credentials()
    await create_new_user_with_email(email=credentials.get("email"))
    users = await service_role_api_client().list_users()
    assert users
    emails = [user.email for user in users]
    assert emails
    assert credentials.get("email") in emails


async def test_get_user_fetches_a_user_by_their_access_token():
    credentials = mock_user_credentials()
    auth_client_with_session_current_user = auth_client_with_session()
    response = await auth_client_with_session_current_user.sign_up(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
        }
    )
    assert response.session
    response = await auth_client_with_session_current_user.get_user()
    assert response.user.email == credentials.get("email")


async def test_get_user_by_id_should_a_registered_user_given_its_user_identifier():
    credentials = mock_user_credentials()
    user = await create_new_user_with_email(email=credentials.get("email"))
    assert user.id
    response = await service_role_api_client().get_user_by_id(user.id)
    assert response.user.email == credentials.get("email")
