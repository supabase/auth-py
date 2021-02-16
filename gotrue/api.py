import json
from typing import Any, Dict

import requests

from gotrue.lib.constants import COOKIE_OPTIONS


def to_dict(request_response) -> Dict[str, Any]:
    """Wrap up request_response to user-friendly dict."""
    return {**request_response.json(), "status_code": request_response.status_code}


class GoTrueApi:
    def __init__(
        self, url: str, headers: Dict[str, Any], cookie_options: Dict[str, Any]
    ):
        """Initialise API class."""
        self.url = url
        self.headers = headers
        self.cookie_options = {**COOKIE_OPTIONS, **cookie_options}

    def sign_up_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Creates a new user using their email address

        Parameters
        ----------
        email : str
            The user's email address.
        password : str
            The user's password.

        Returns
        -------
        request : dict of any
            The user or error message returned by the supabase backend.
        """
        credentials = {"email": email, "password": password}
        request = requests.post(
            f"{self.url}/signup", json.dumps(credentials), headers=self.headers
        )
        return to_dict(request)

    def sign_in_with_email(self, email: str, password: str) -> Dict[str, Any]:
        """Logs in an existing user using their email address.

        Parameters
        ----------
        email : str
            The user's email address.
        password : str
            The user's password.

        Returns
        -------
        request : dict of any
            The user or error message returned by the supabase backend.
        """
        credentials = {"email": email, "password": password}
        request = requests.post(
            f"{self.url}/token?grant_type=password",
            json.dumps(credentials),
            headers=self.headers,
        )
        return to_dict(request)

    def send_magic_link_email(self, email: str) -> Dict[str, Any]:
        """Sends a magic login link to an email address.

        Parameters
        ----------
        email : str
            The user's email address.

        Returns
        -------
        request : dict of any
            The user or error message returned by the supabase backend.
        """
        credentials = {"email": email}
        request = requests.post(
            f"{self.url}/magiclink", json.dumps(credentials), headers=self.headers
        )
        return to_dict(request)

    def invite_user_by_email(self, email: str) -> Dict[str, Any]:
        """Sends an invite link to an email address.

        Parameters
        ----------
        email : str
            The user's email address.

        Returns
        -------
        request : dict of any
            The invite or error message returned by the supabase backend.
        """
        credentials = {"email": email}
        request = requests.post(
            f"{self.url}/invite", json.dumps(credentials), headers=self.headers
        )
        return to_dict(request)

    def reset_password_for_email(self, email: str) -> Dict[str, Any]:
        """Sends a reset request to an email address.

        Parameters
        ----------
        email : str
            The user's email address.

        Returns
        -------
        request : dict of any
            The password reset status or error message returned by the supabase
            backend.
        """
        credentials = {"email": email}
        request = requests.post(
            f"{self.url}/recover", json.dumps(credentials), headers=self.headers
        )
        return to_dict(request)

    def _create_request_headers(self, jwt: str) -> Dict[str, str]:
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

    def sign_out(self, jwt: str):
        """Removes a logged-in session.

        Parameters
        ----------
        jwt : str
             A valid, logged-in JWT.
        """
        requests.post(f"{self.url}/logout", headers=self._create_request_headers(jwt))

    def get_url_for_provider(self, provider: str) -> str:
        """Generates the relevant login URL for a third-party provider."""
        return f"{self.url}/authorize?provider={provider}"

    def get_user(self, jwt: str) -> Dict[str, Any]:
        """Gets the user details

        Parameters
        ----------
        jwt : str
             A valid, logged-in JWT.

        Returns
        -------
        request : dict of any
            The user or error message returned by the supabase backend.
        """
        request = requests.get(
            f"{self.url}/user", headers=self._create_request_headers(jwt)
        )
        return to_dict(request)

    def update_user(self, jwt: str, **attributes) -> Dict[str, Any]:
        """Updates the user data through the attributes kwargs."""
        request = requests.put(
            f"{self.url}/user",
            json.dumps(attributes),
            headers=self._create_request_headers(jwt),
        )
        return to_dict(request)

    def refresh_access_token(self, refresh_token: str) -> Dict[str, Any]:
        """Generates a new JWT.

        Parameters
        ----------
        refresh_token : str
            A valid refresh token that was returned on login.
        """
        request = requests.post(
            f"{self.url}/token?grant_type=refresh_token",
            json.dumps({"refresh_token": refresh_token}),
            headers=self.headers,
        )
        return to_dict(request)

    def set_auth_cookie(req, res):
        """Stub for parity with JS api."""
        raise NotImplementedError("set_auth_cookie not implemented.")

    def get_user_by_cookie(req):
        """Stub for parity with JS api."""
        raise NotImplementedError("get_user_by_cookie not implemented.")
