from typing import Iterable, Optional

import pytest
from faker import Faker

from gotrue import SyncGoTrueClient
from gotrue.exceptions import APIError
from gotrue.types import Session, User, UserAttributes

GOTRUE_URL = "http://localhost:9998"
TEST_TWILIO = False


@pytest.fixture(name="client")
def create_client() -> Iterable[SyncGoTrueClient]:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=True,
    ) as client:
        yield client


@pytest.fixture(name="client_with_session")
def create_client_with_session() -> Iterable[SyncGoTrueClient]:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


@pytest.fixture(name="new_client")
def create_new_client() -> Iterable[SyncGoTrueClient]:
    with SyncGoTrueClient(
        url=GOTRUE_URL,
        auto_refresh_token=False,
        persist_session=False,
    ) as client:
        yield client


fake = Faker()

email = f"client_ac_enabled_{fake.email().lower()}"
set_session_email = f"client_ac_session_{fake.email().lower()}"
refresh_token_email = f"client_refresh_token_signin_{fake.email().lower()}"
password = fake.password()
access_token: Optional[str] = None


@pytest.mark.asyncio
def test_sign_up(client: SyncGoTrueClient):
    try:
        response = client.sign_up(
            email=email,
            password=password,
            data={"status": "alpha"},
        )
        assert isinstance(response, Session)
        global access_token
        access_token = response.access_token
        assert response.access_token
        assert response.refresh_token
        assert response.expires_in
        assert response.expires_at
        assert response.user
        assert response.user.id
        assert response.user.email == email
        assert response.user.email_confirmed_at
        assert response.user.last_sign_in_at
        assert response.user.created_at
        assert response.user.updated_at
        assert response.user.app_metadata
        assert response.user.app_metadata.get("provider") == "email"
        assert response.user.user_metadata
        assert response.user.user_metadata.get("status") == "alpha"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_set_session_should_return_no_error(
    client_with_session: SyncGoTrueClient,
):
    try:
        response = client_with_session.sign_up(
            email=set_session_email,
            password=password,
        )
        assert isinstance(response, Session)
        assert response.refresh_token
        client_with_session.set_session(refresh_token=response.refresh_token)
        data = {"hello": "world"}
        response = client_with_session.update(attributes=UserAttributes(data=data))
        assert response.user_metadata == data
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_sign_up_the_same_user_twice_should_throw_an_error(
    client: SyncGoTrueClient,
):
    expected_error_message = "User already registered"
    try:
        client.sign_up(
            email=email,
            password=password,
        )
        assert False
    except APIError as e:
        assert expected_error_message in e.msg
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_set_auth_should_set_the_auth_headers_on_a_new_client(
    new_client: SyncGoTrueClient,
):
    try:
        assert access_token
        new_client.set_auth(access_token=access_token)
        assert new_client.current_session
        assert new_client.current_session.access_token == access_token
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(
    on=[test_set_auth_should_set_the_auth_headers_on_a_new_client.__name__]
)
def test_set_auth_should_set_the_auth_headers_on_a_new_client_and_recover(
    new_client: SyncGoTrueClient,
):
    try:
        assert access_token
        new_client.init_recover()
        new_client.set_auth(access_token=access_token)
        assert new_client.current_session
        assert new_client.current_session.access_token == access_token
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_sign_in(client: SyncGoTrueClient):
    try:
        response = client.sign_in(email=email, password=password)
        assert isinstance(response, Session)
        assert response.access_token
        assert response.refresh_token
        assert response.expires_in
        assert response.expires_at
        assert response.user
        assert response.user.id
        assert response.user.email == email
        assert response.user.email_confirmed_at
        assert response.user.last_sign_in_at
        assert response.user.created_at
        assert response.user.updated_at
        assert response.user.app_metadata
        assert response.user.app_metadata.get("provider") == "email"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_refresh_token(client_with_session: SyncGoTrueClient):
    try:
        response = client_with_session.sign_up(
            email=refresh_token_email,
            password=password,
        )
        assert isinstance(response, Session)
        assert response.refresh_token
        response2 = client_with_session.sign_in(refresh_token=response.refresh_token)
        assert isinstance(response2, Session)
        assert response2.access_token
        assert response2.refresh_token
        assert response2.expires_in
        assert response2.expires_at
        assert response2.user
        assert response2.user.id
        assert response2.user.email == refresh_token_email
        assert response2.user.email_confirmed_at
        assert response2.user.last_sign_in_at
        assert response2.user.created_at
        assert response2.user.updated_at
        assert response2.user.app_metadata
        assert response2.user.app_metadata.get("provider") == "email"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_in.__name__])
def test_get_user(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.user()
        assert isinstance(response, User)
        assert response.id
        assert response.email == email
        assert response.email_confirmed_at
        assert response.last_sign_in_at
        assert response.created_at
        assert response.updated_at
        assert response.app_metadata
        provider = response.app_metadata.get("provider")
        assert provider == "email"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_in.__name__])
def test_get_session(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.session()
        assert isinstance(response, Session)
        assert response.access_token
        assert response.refresh_token
        assert response.expires_in
        assert response.expires_at
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_in.__name__])
def test_update_user(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.update(attributes=UserAttributes(data={"hello": "world"}))
        assert isinstance(response, User)
        assert response.id
        assert response.email == email
        assert response.email_confirmed_at
        assert response.last_sign_in_at
        assert response.created_at
        assert response.updated_at
        assert response.user_metadata
        assert response.user_metadata.get("hello") == "world"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_update_user.__name__])
def test_get_user_after_update(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.user()
        assert isinstance(response, User)
        assert response.id
        assert response.email == email
        assert response.email_confirmed_at
        assert response.last_sign_in_at
        assert response.created_at
        assert response.updated_at
        assert response.user_metadata
        assert response.user_metadata.get("hello") == "world"
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_get_user_after_update.__name__])
def test_sign_out(client: SyncGoTrueClient):
    try:
        client.init_recover()
        client.sign_out()
        response = client.session()
        assert response is None
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_out.__name__])
def test_get_user_after_sign_out(client: SyncGoTrueClient):
    try:
        client.init_recover()
        response = client.user()
        assert not response
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_out.__name__])
def test_get_update_user_after_sign_out(client: SyncGoTrueClient):
    expected_error_message = "Not logged in."
    try:
        client.init_recover()
        client.update(attributes=UserAttributes(data={"hello": "world"}))
        assert False
    except ValueError as e:
        assert str(e) == expected_error_message
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_get_user_after_sign_out.__name__])
def test_sign_in_with_the_wrong_password(client: SyncGoTrueClient):
    try:
        client.sign_in(email=email, password=password + "2")
        assert False
    except APIError:
        assert True
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_up_with_password_none(client: SyncGoTrueClient):
    expected_error_message = "Password must be defined, can't be None."
    try:
        client.sign_up(email=email)
        assert False
    except ValueError as e:
        assert str(e) == expected_error_message
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_up_with_email_and_phone_none(client: SyncGoTrueClient):
    expected_error_message = "Email or phone must be defined, both can't be None."
    try:
        client.sign_up(password=password)
        assert False
    except ValueError as e:
        assert str(e) == expected_error_message
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_all_nones(client: SyncGoTrueClient):
    expected_error_message = (
        "Email, phone, refresh_token, or provider must be defined, "
        "all can't be None."
    )
    try:
        client.sign_in()
        assert False
    except ValueError as e:
        assert str(e) == expected_error_message
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_sign_in_with_magic_link(client: SyncGoTrueClient):
    try:
        response = client.sign_in(email=email)
        assert response is None
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_sign_up.__name__])
def test_get_session_from_url(client: SyncGoTrueClient):
    try:
        assert access_token
        dummy_url = (
            "https://localhost"
            f"?access_token={access_token}"
            "&refresh_token=refresh_token"
            "&token_type=bearer"
            "&expires_in=3600"
            "&type=recovery"
        )
        response = client.get_session_from_url(url=dummy_url, store_session=True)
        assert isinstance(response, Session)
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
def test_get_session_from_url_errors(client: SyncGoTrueClient):
    try:
        dummy_url = "https://localhost"
        error_description = fake.email()
        try:
            client.get_session_from_url(
                url=dummy_url + f"?error_description={error_description}"
            )
            assert False
        except APIError as e:
            assert e.code == 400
            assert e.msg == error_description
        try:
            client.get_session_from_url(url=dummy_url)
            assert False
        except APIError as e:
            assert e.code == 400
            assert e.msg == "No access_token detected."
        dummy_url += "?access_token=access_token"
        try:
            client.get_session_from_url(url=dummy_url)
            assert False
        except APIError as e:
            assert e.code == 400
            assert e.msg == "No refresh_token detected."
        dummy_url += "&refresh_token=refresh_token"
        try:
            client.get_session_from_url(url=dummy_url)
            assert False
        except APIError as e:
            assert e.code == 400
            assert e.msg == "No token_type detected."
        dummy_url += "&token_type=bearer"
        try:
            client.get_session_from_url(url=dummy_url)
            assert False
        except APIError as e:
            assert e.code == 400
            assert e.msg == "No expires_in detected."
        dummy_url += "&expires_in=str"
        try:
            client.get_session_from_url(url=dummy_url)
            assert False
        except APIError as e:
            assert e.code == 400
            assert e.msg == "Invalid expires_in."
    except Exception as e:
        assert False, str(e)


@pytest.mark.asyncio
@pytest.mark.depends(on=[test_get_update_user_after_sign_out.__name__])
def test_refresh_session(client: SyncGoTrueClient):
    try:
        response = client.sign_in(email=email, password=password)
        assert isinstance(response, Session)
        assert response.refresh_token
        response = client.set_session(refresh_token=response.refresh_token)
        assert isinstance(response, Session)
        response = client.refresh_session()
        assert isinstance(response, Session)
        client.sign_out()
        try:
            client.refresh_session()
            assert False
        except ValueError as e:
            assert str(e) == "Not logged in."
    except Exception as e:
        assert False, str(e)
