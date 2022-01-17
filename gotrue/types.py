from __future__ import annotations

from datetime import datetime
from enum import Enum
from time import time
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

from httpx import Response
from pydantic import BaseModel, root_validator

from gotrue.helpers import check_response

T = TypeVar("T", bound=BaseModel)


def determine_session_or_user_model_from_response(
    response: Response,
) -> Union[Type[Session], Type[User]]:
    return Session if "access_token" in response.json() else User


class BaseModelFromResponse(BaseModel):
    @classmethod
    def parse_response(cls: Type[T], response: Response) -> T:
        check_response(response)
        return cls.parse_obj(response.json())


class CookieOptions(BaseModelFromResponse):
    name: str
    """The name of the cookie. Defaults to `sb:token`."""
    lifetime: int
    """The cookie lifetime (expiration) in seconds. Set to 8 hours by default."""
    domain: str
    """The cookie domain this should run on.
    Leave it blank to restrict it to your domain."""
    path: str
    same_site: str
    """SameSite configuration for the session cookie.
    Defaults to 'lax', but can be changed to 'strict' or 'none'.
    Set it to false if you want to disable the SameSite setting."""


class Identity(BaseModelFromResponse):
    id: UUID
    user_id: UUID
    provider: str
    created_at: datetime
    updated_at: datetime
    identity_data: Optional[Dict[str, Any]] = None
    last_sign_in_at: Optional[datetime] = None


class User(BaseModelFromResponse):
    app_metadata: Dict[str, Any]
    aud: str
    """The user's audience. Use audiences to group users."""
    created_at: datetime
    id: UUID
    user_metadata: Dict[str, Any]
    identities: Optional[List[Identity]] = None
    confirmation_sent_at: Optional[datetime] = None
    action_link: Optional[str] = None
    last_sign_in_at: Optional[datetime] = None
    phone: Optional[str] = None
    phone_confirmed_at: Optional[datetime] = None
    recovery_sent_at: Optional[datetime] = None
    role: Optional[str] = None
    updated_at: Optional[datetime] = None
    email_confirmed_at: Optional[datetime] = None
    confirmed_at: Optional[datetime] = None
    invited_at: Optional[datetime] = None
    email: Optional[str] = None
    new_email: Optional[str] = None
    email_change_sent_at: Optional[datetime] = None
    new_phone: Optional[str] = None
    phone_change_sent_at: Optional[datetime] = None


class UserAttributes(BaseModelFromResponse):
    email: Optional[str] = None
    """The user's email."""
    password: Optional[str] = None
    """The user's password."""
    email_change_token: Optional[str] = None
    """An email change token."""
    data: Optional[Any] = None
    """A custom data object. Can be any JSON."""


class Session(BaseModelFromResponse):
    access_token: str
    token_type: str
    expires_at: Optional[int] = None
    """A timestamp of when the token will expire. Returned when a login is confirmed."""
    expires_in: Optional[int] = None
    """The number of seconds until the token expires (since it was issued).
    Returned when a login is confirmed."""
    provider_token: Optional[str] = None
    refresh_token: Optional[str] = None
    user: Optional[User] = None

    @root_validator
    def validator(cls, values: dict) -> dict:
        expires_in = values.get("expires_in")
        if expires_in and not values.get("expires_at"):
            values["expires_at"] = round(time()) + expires_in
        return values


class AuthChangeEvent(str, Enum):
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"
    SIGNED_IN = "SIGNED_IN"
    SIGNED_OUT = "SIGNED_OUT"
    TOKEN_REFRESHED = "TOKEN_REFRESHED"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"


class Subscription(BaseModelFromResponse):
    id: UUID
    """The subscriber UUID. This will be set by the client."""
    callback: Callable[[AuthChangeEvent, Optional[Session]], None]
    """The function to call every time there is an event."""
    unsubscribe: Callable[[], None]
    """Call this to remove the listener."""


class Provider(str, Enum):
    apple = "apple"
    azure = "azure"
    bitbucket = "bitbucket"
    discord = "discord"
    facebook = "facebook"
    github = "github"
    gitlab = "gitlab"
    google = "google"
    notion = "notion"
    slack = "slack"
    spotify = "spotify"
    twitter = "twitter"
    twitch = "twitch"


class LinkType(str, Enum):
    """The type of link."""

    signup = "signup"
    magiclink = "magiclink"
    recovery = "recovery"
    invite = "invite"
