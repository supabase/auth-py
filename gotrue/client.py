"""
client.py
====================================
core module of the project
"""
import datetime
import functools
import json
import re
import uuid
from typing import Any, Callable, Dict, Optional

from gotrue.api import GoTrueApi
from gotrue.lib.constants import GOTRUE_URL, STORAGE_KEY


HTTPRegexp = "/^http://"
defaultApiURL = "/.netlify/identity"


class Client:
    def __init__(
        self,
        headers: Dict[str, str],
        url: str = GOTRUE_URL,
        detect_session_in_url: bool = True,
        auto_refresh_token: bool = True,
        persist_session: bool = True,
        local_storage: Dict[str, Any] = {},
        cookie_options: Dict[str, Any] = {},
    ):
        """Create a new client for use in the browser.

        url
            The URL of the GoTrue server.
        headers
            Any additional headers to send to the GoTrue server.
        detectSessionInUrl
            Set to "true" if you want to automatically detects OAuth grants in
            the URL and signs in the user.
        autoRefreshToken
            Set to "true" if you want to automatically refresh the token before
            expiring.
        persistSession
            Set to "true" if you want to automatically save the user session
            into local storage.
        localStorage
        """
        if re.match(HTTPRegexp, url):
            print(
                "Warning:\n\nDO NOT USE HTTP IN PRODUCTION FOR GOTRUE EVER!\n"
                "GoTrue REQUIRES HTTPS to work securely."
            )
        self.state_change_emitters: Dict[str, Any] = {}
        self.current_user = None
        self.current_session = None
        self.auto_refresh_token = auto_refresh_token
        self.persist_session = persist_session
        self.local_storage: Dict[str, Any] = {}
        self.api = GoTrueApi(url=url, headers=headers, cookie_options=cookie_options)
        self._recover_session()

    def sign_up(self, email: str, password: str):
        """Creates a new user.

        Parameters
        ---------
        email : str
            The user's email address.
        password : str
            The user's password.
        """
        self._remove_session()
        data = self.api.sign_up_with_email(email, password)
        if "expires_in" in data and "user" in data:
            # The user has confirmed their email or the underlying DB doesn't
            # require email confirmation.
            self._save_session(data)
            self._notify_all_subscribers("SIGNED_IN")
        return data

    def sign_in(
        self,
        email: Optional[str] = None,
        password: Optional[str] = None,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Log in an exisiting user, or login via a third-party provider."""
        self._remove_session()
        if email is not None and password is None:
            data = self.api.send_magic_link_email(email)
        elif email is not None and password is not None:
            data = self._handle_email_sign_in(email, password)
        elif provider is not None:
            data = self._handle_provider_sign_in(provider)
        else:
            raise ValueError("Email or provider must be defined, both can't be None.")
        return data

    def user(self) -> Optional[Dict[str, Any]]:
        """Returns the user data, if there is a logged in user."""
        return self.current_user

    def session(self) -> Optional[Dict[str, Any]]:
        """Returns the session data, if there is an active session."""
        return self.current_session

    def refresh_session(self) -> Dict[str, Any]:
        """Force refreshes the session.

        Force refreshes the session including the user data incase it was
        updated in a different session.
        """
        if self.current_session is None or "access_token" not in self.current_session:
            raise ValueError("Not logged in.")
        self._call_refresh_token()
        data = self.api.get_user(self.current_session["access_token"])
        self.current_user = data
        return data

    def update(self, **attributes) -> Dict[str, Any]:
        """Updates user data, if there is a logged in user."""
        if self.current_session is None or not self.current_session.get("access_token"):
            raise ValueError("Not logged in.")
        data = self.api.update_user(self.current_session["access_token"], **attributes)
        self.current_user = data
        self._notify_all_subscribers("USER_UPDATED")
        return data

    def get_session_from_url(self, store_session: bool):
        """Gets the session data from a URL string."""
        raise NotImplementedError(
            "This method is a stub and is only required by the JS client."
        )

    def sign_out(self):
        """Log the user out."""
        if self.current_session is not None and "access_token" in self.current_session:
            self.api.sign_out(self.current_session["access_token"])
        self._remove_session()
        self._notify_all_subscribers("SIGNED_OUT")

    def on_auth_state_change(
        self, callback: Callable[[str, Optional[Dict[str, Any]]], Any],
    ):
        """"""
        unique_id: str = str(uuid.uuid4())
        subscription: Dict[str, Any] = {
            "id": unique_id,
            "callback": callback,
            "unsubscribe": functools.partial(
                self.state_change_emitters.pop, id=unique_id
            ),
        }
        self.state_change_emitters[unique_id] = subscription
        return subscription

    def _handle_email_sign_in(self, email: str, password: str) -> Dict[str, Any]:
        """Sign in with email and password."""
        data = self.api.sign_in_with_email(email, password)
        if (
            data is not None
            and data.get("user") is not None
            and "confirmed_at" in data["user"]
        ):
            self._save_session(data)
            self._notify_all_subscribers("SIGNED_IN")
        return data

    def _handle_provider_sign_in(self, provider):
        """Sign in with provider."""
        raise NotImplementedError("Not implemeted for Python client.")

    def _save_session(self, session):
        """Save session to client."""
        required_keys = ["user", "expires_in"]
        if any(key not in session for key in required_keys):
            raise ValueError(
                f"Session not defined as expected, one of {required_keys} not "
                f"present in session dict..")
        self.current_session = session
        self.current_user = session["user"]
        token_expiry_seconds = session["expires_in"]
        if self.auto_refresh_token and token_expiry_seconds is not None:
            self._set_timeout(
                self._call_refresh_token, (token_expiry_seconds - 60) * 1000
            )
        if self.persist_session:
            self._persist_session(self.current_session, token_expiry_seconds)

    def _persist_session(self, current_session, seconds_to_expiry: int):
        timenow_seconds: int = int(round(datetime.datetime.now().timestamp()))
        expires_at: int = timenow_seconds + seconds_to_expiry
        data = {
            "current_session": current_session,
            "expires_at": expires_at,
        }
        self.local_storage[STORAGE_KEY] = json.dumps(data)

    def _remove_session(self):
        """Remove the session."""
        self.current_session = None
        self.current_user = None
        self.local_storage.pop(STORAGE_KEY, None)

    def _recover_session(self):
        """Kept as a stub for pairity with the JS client. Only required for
        React Native.
        """
        pass

    def _call_refresh_token(self, refresh_token: Optional[str] = None):
        logged_in: bool = self.current_session is not None and "access_token" in self.current_session
        if refresh_token is None and logged_in:
            refresh_token = self.current_session["refresh_token"]
        elif refresh_token is None:
            raise ValueError("No current session and refresh_token not supplied.")
        data = self.api.refresh_access_token(refresh_token)
        if "access_token" in data:
            self.current_session = data
            self.current_user = data["user"]
            self._notify_all_subscribers("SIGNED_IN")
            token_expiry_seconds: int = data["expires_in"]
            if self.auto_refresh_token and token_expiry_seconds is not None:
                self._set_timeout(
                    self._call_refresh_token, (token_expiry_seconds - 60) * 1000
                )
            if self.persist_session:
                self._persist_session(self.current_session, token_expiry_seconds)
        return data

    def _notify_all_subscribers(self, event: str):
        """Notify all subscribers that auth event happened."""
        for value in self.state_change_emitters.values():
            value["callback"](event, self.current_session)

    def _set_timeout(*args, **kwargs):
        """"""
        # TODO(fedden): Implement JS equivalent of setTimeout method.
        pass
