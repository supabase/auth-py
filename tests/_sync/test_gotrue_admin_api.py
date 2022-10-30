from .clients import service_role_api_client
from .utils import (
    create_new_user_with_email,
    mock_app_metadata,
    mock_user_credentials,
    mock_user_metadata,
)


def test_create_user_should_create_a_new_user():
    credentials = mock_user_credentials()
    response = create_new_user_with_email(email=credentials.get("email"))
    assert response.email == credentials.get("email")


def test_create_user_with_user_metadata():
    user_metadata = mock_user_metadata()
    credentials = mock_user_credentials()
    response = service_role_api_client().create_user(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
            "user_metadata": user_metadata,
        }
    )
    assert response.user.email == credentials.get("email")
    assert response.user.user_metadata == user_metadata
    assert "profile_image" in response.user.user_metadata


def test_create_user_with_app_metadata():
    app_metadata = mock_app_metadata()
    credentials = mock_user_credentials()
    response = service_role_api_client().create_user(
        {
            "email": credentials.get("email"),
            "password": credentials.get("password"),
            "app_metadata": app_metadata,
        }
    )
    assert response.user.email == credentials.get("email")
    assert "provider" in response.user.app_metadata
    assert "providers" in response.user.app_metadata


def test_create_user_with_user_and_app_metadata():
    user_metadata = mock_user_metadata()
    app_metadata = mock_app_metadata()
    credentials = mock_user_credentials()
    response = service_role_api_client().create_user(
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
