from __future__ import annotations

from typing import Any, Optional, Union

from ..helpers import encode_uri_component, parse_response, parse_session_or_user
from ..http_clients import AsyncClient
from ..types import CookieOptions, LinkType, Provider, Session, User, UserAttributes


class AsyncGoTrueAPI:
    def __init__(
        self,
        *,
        url: str,
        headers: dict[str, str],
        cookie_options: CookieOptions,
    ) -> None:
        """Initialise API class."""
        self.url = url
        self.headers = headers
        self.cookie_options = cookie_options
        self.http_client = AsyncClient()

    async def __aenter__(self) -> AsyncGoTrueAPI:
        return self

    async def __aexit__(self, exc_t, exc_v, exc_tb) -> None:
        await self.close()

    async def close(self) -> None:
        await self.http_client.aclose()

    async def sign_up_with_email(
        self,
        *,
        email: str,
        password: str,
        redirect_to: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> Union[Session, User]:
        """Creates a new user using their email address.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str
            The password of the user.
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.
        data : Optional[dict[str, Any]]
            Optional user metadata.

        Returns
        -------
        response : Union[Session, User]
            A logged-in session if the server has "autoconfirm" ON
            A user if the server has "autoconfirm" OFF

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = ""
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            query_string = f"?redirect_to={redirect_to_encoded}"
        data = {"email": email, "password": password, "data": data}
        url = f"{self.url}/signup{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, parse_session_or_user)

    async def sign_in_with_email(
        self,
        *,
        email: str,
        password: str,
        redirect_to: Optional[str] = None,
    ) -> Session:
        """Logs in an existing user using their email address.

        Parameters
        ----------
        email : str
            The email address of the user.
        password : str
            The password of the user.
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.

        Returns
        -------
        response : Session
            A logged-in session

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = "?grant_type=password"
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            query_string += f"&redirect_to={redirect_to_encoded}"
        data = {"email": email, "password": password}
        url = f"{self.url}/token{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, Session.from_dict)

    async def sign_up_with_phone(
        self,
        *,
        phone: str,
        password: str,
        data: Optional[dict[str, Any]] = None,
    ) -> Union[Session, User]:
        """Signs up a new user using their phone number and a password.

        Parameters
        ----------
        phone : str
            The phone number of the user.
        password : str
            The password of the user.
        data : Optional[dict[str, Any]]
            Optional user metadata.

        Returns
        -------
        response : Union[Session, User]
            A logged-in session if the server has "autoconfirm" ON
            A user if the server has "autoconfirm" OFF

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        data = {"phone": phone, "password": password, "data": data}
        url = f"{self.url}/signup"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, parse_session_or_user)

    async def sign_in_with_phone(
        self,
        *,
        phone: str,
        password: str,
    ) -> Session:
        """Logs in an existing user using their phone number and password.

        Parameters
        ----------
        phone : str
            The phone number of the user.
        password : str
            The password of the user.

        Returns
        -------
        response : Session
            A logged-in session

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = "?grant_type=password"
        data = {"phone": phone, "password": password}
        url = f"{self.url}/token{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, Session.from_dict)

    async def send_magic_link_email(
        self,
        *,
        email: str,
        redirect_to: Optional[str] = None,
    ) -> None:
        """Sends a magic login link to an email address.

        Parameters
        ----------
        email : str
            The email address of the user.
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = ""
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            query_string = f"?redirect_to={redirect_to_encoded}"
        data = {"email": email}
        url = f"{self.url}/magiclink{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, lambda _: None)

    async def send_mobile_otp(self, *, phone: str) -> None:
        """Sends a mobile OTP via SMS. Will register the account if it doesn't already exist

        Parameters
        ----------
        phone : str
            The user's phone number WITH international prefix

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        data = {"phone": phone}
        url = f"{self.url}/otp"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, lambda _: None)

    async def verify_mobile_otp(
        self,
        *,
        phone: str,
        token: str,
        redirect_to: Optional[str] = None,
    ) -> Union[Session, User]:
        """Send User supplied Mobile OTP to be verified

        Parameters
        ----------
        phone : str
            The user's phone number WITH international prefix
        token : str
            Token that user was sent to their mobile phone
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.

        Returns
        -------
        response : Union[Session, User]
            A logged-in session if the server has "autoconfirm" ON
            A user if the server has "autoconfirm" OFF

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        data = {
            "phone": phone,
            "token": token,
            "type": "sms",
        }
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            data["redirect_to"] = redirect_to_encoded
        url = f"{self.url}/verify"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, parse_session_or_user)

    async def invite_user_by_email(
        self,
        *,
        email: str,
        redirect_to: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> User:
        """Sends an invite link to an email address.

        Parameters
        ----------
        email : str
            The email address of the user.
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.
        data : Optional[dict[str, Any]]
            Optional user metadata.

        Returns
        -------
        response : User
            A user

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = ""
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            query_string = f"?redirect_to={redirect_to_encoded}"
        data = {"email": email, "data": data}
        url = f"{self.url}/invite{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, User.from_dict)

    async def reset_password_for_email(
        self,
        *,
        email: str,
        redirect_to: Optional[str] = None,
    ) -> None:
        """Sends a reset request to an email address.

        Parameters
        ----------
        email : str
            The email address of the user.
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = ""
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            query_string = f"?redirect_to={redirect_to_encoded}"
        data = {"email": email}
        url = f"{self.url}/recover{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, lambda _: None)

    def __create_request_headers(self, *, jwt: str) -> dict[str, str]:
        """Create temporary object.

        Create a temporary object with all configured headers and adds the
        Authorization token to be used on request methods.

        Parameters
        ----------
        jwt : str
            A valid, logged-in JWT.

        Returns
        -------
        headers : dict of str
            The headers required for a successful request statement with the
            supabase backend.
        """
        headers = {**self.headers}
        headers["Authorization"] = f"Bearer {jwt}"
        return headers

    async def sign_out(self, *, jwt: str) -> None:
        """Removes a logged-in session.

        Parameters
        ----------
        jwt : str
            A valid, logged-in JWT.
        """
        headers = self.__create_request_headers(jwt=jwt)
        url = f"{self.url}/logout"
        await self.http_client.post(url, headers=headers)

    async def get_url_for_provider(
        self,
        *,
        provider: Provider,
        redirect_to: Optional[str] = None,
        scopes: Optional[str] = None,
    ) -> str:
        """Generates the relevant login URL for a third-party provider.

        Parameters
        ----------
        provider : Provider
            One of the providers supported by GoTrue.
        redirect_to : Optional[str]
            A URL or mobile address to send the user to after they are confirmed.
        scopes : Optional[str]
            A space-separated list of scopes granted to the OAuth application.

        Returns
        -------
        url : str
            The URL to redirect the user to.

        Raises
        ------
        error : APIError
            If an error occurs
        """
        url_params = [f"provider={encode_uri_component(provider)}"]
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            url_params.append(f"redirect_to={redirect_to_encoded}")
        if scopes:
            url_params.append(f"scopes={encode_uri_component(scopes)}")
        return f"{self.url}/authorize?{'&'.join(url_params)}"

    async def get_user(self, *, jwt: str) -> User:
        """Gets the user details.

        Parameters
        ----------
        jwt : str
            A valid, logged-in JWT.

        Returns
        -------
        response : User
            A user

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.__create_request_headers(jwt=jwt)
        url = f"{self.url}/user"
        response = await self.http_client.get(url, headers=headers)
        return parse_response(response, User.from_dict)

    async def update_user(
        self,
        *,
        jwt: str,
        attributes: UserAttributes,
    ) -> User:
        """
        Updates the user data.

        Parameters
        ----------
        jwt : str
            A valid, logged-in JWT.
        attributes : UserAttributes
            The data you want to update.

        Returns
        -------
        response : User
            A user

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.__create_request_headers(jwt=jwt)
        data = attributes.to_dict()
        url = f"{self.url}/user"
        response = await self.http_client.put(url, json=data, headers=headers)
        return parse_response(response, User.from_dict)

    async def delete_user(self, *, uid: str, jwt: str) -> User:
        """Delete a user. Requires a `service_role` key.

        This function should only be called on a server.
        Never expose your `service_role` key in the browser.

        Parameters
        ----------
        uid : str
            The user uid you want to remove.
        jwt : str
            A valid, logged-in JWT.

        Returns
        -------
        response : User
            A user

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.__create_request_headers(jwt=jwt)
        url = f"{self.url}/admin/users/${uid}"
        response = await self.http_client.delete(url, headers=headers)
        return parse_response(response, User.from_dict)

    async def refresh_access_token(self, *, refresh_token: str) -> Session:
        """Generates a new JWT.

        Parameters
        ----------
        refresh_token : str
            A valid refresh token that was returned on login.

        Returns
        -------
        response : Session
            A session

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        query_string = "?grant_type=refresh_token"
        data = {"refresh_token": refresh_token}
        url = f"{self.url}/token{query_string}"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, Session.from_dict)

    async def generate_link(
        self,
        *,
        type: LinkType,
        email: str,
        password: Optional[str] = None,
        redirect_to: Optional[str] = None,
        data: Optional[dict[str, Any]] = None,
    ) -> Union[Session, User]:
        """
        Generates links to be sent via email or other.

        Parameters
        ----------
        type : LinkType
            The link type ("signup" or "magiclink" or "recovery" or "invite").
        email : str
            The user's email.
        password : Optional[str]
            User password. For signup only.
        redirect_to : Optional[str]
            The link type ("signup" or "magiclink" or "recovery" or "invite").
        data : Optional[dict[str, Any]]
            Optional user metadata. For signup only.

        Returns
        -------
        response : Union[Session, User]
            A logged-in session if the server has "autoconfirm" ON
            A user if the server has "autoconfirm" OFF

        Raises
        ------
        error : APIError
            If an error occurs
        """
        headers = self.headers
        data = {
            "type": type,
            "email": email,
            "data": data,
        }
        if password:
            data["password"] = password
        if redirect_to:
            redirect_to_encoded = encode_uri_component(redirect_to)
            data["redirect_to"] = redirect_to_encoded
        url = f"{self.url}/admin/generate_link"
        response = await self.http_client.post(url, json=data, headers=headers)
        return parse_response(response, parse_session_or_user)

    async def set_auth_cookie(self, *, req, res):
        """Stub for parity with JS api."""
        raise NotImplementedError("set_auth_cookie not implemented.")

    async def get_user_by_cookie(self, *, req):
        """Stub for parity with JS api."""
        raise NotImplementedError("get_user_by_cookie not implemented.")
