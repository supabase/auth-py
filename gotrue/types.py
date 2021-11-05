from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import Enum
from inspect import signature
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


def parse_dict(cls: Type[T], **json: dict) -> T:
    cls_fields = {field for field in signature(cls).parameters}
    native_args, new_args = {}, {}
    for name, val in json.items():
        if name in cls_fields:
            native_args[name] = val
        else:
            new_args[name] = val
    ret = cls(**native_args)
    for new_name, new_val in new_args.items():
        setattr(ret, new_name, new_val)
    return ret


@dataclass
class APIError(BaseException):
    msg: str
    code: int

    def __post_init__(self) -> None:
        self.msg = str(self.msg)
        self.code = int(str(self.code))

    @classmethod
    def from_dict(cls, data: dict) -> APIError:
        if "msg" in data and "code" in data:
            return APIError(
                msg=data["msg"],
                code=data["code"],
            )
        if "error" in data and "error_description" in data:
            try:
                code = int(data["error"])
            except ValueError:
                code = -1
            return APIError(
                msg=data["error_description"],
                code=code,
            )
        return parse_dict(cls, **data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


class CookieOptions(BaseModel):
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


class Identity(BaseModel):
    id: str
    user_id: str
    provider: str
    created_at: str
    updated_at: str
    identity_data: Optional[Dict[str, Any]] = None
    last_sign_in_at: Optional[str] = None


class User(BaseModel):
    app_metadata: Dict[str, Any]
    aud: str
    created_at: str
    id: str
    user_metadata: Dict[str, Any]
    identities: Optional[List[Identity]] = None
    confirmation_sent_at: Optional[str] = None
    action_link: Optional[str] = None
    last_sign_in_at: Optional[str] = None
    phone: Optional[str] = None
    phone_confirmed_at: Optional[str] = None
    recovery_sent_at: Optional[str] = None
    role: Optional[str] = None
    updated_at: Optional[str] = None
    email_confirmed_at: Optional[str] = None
    confirmed_at: Optional[str] = None
    invited_at: Optional[str] = None
    email: Optional[str] = None
    new_email: Optional[str] = None
    email_change_sent_at: Optional[str] = None
    new_phone: Optional[str] = None
    phone_change_sent_at: Optional[str] = None


class UserAttributes(BaseModel):
    email: Optional[str] = None
    """The user's email."""
    password: Optional[str] = None
    """The user's password."""
    email_change_token: Optional[str] = None
    """An email change token."""
    data: Optional[Any] = None
    """A custom data object. Can be any JSON."""


class Session(BaseModel):
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


class AuthChangeEvent(str, Enum):
    SIGNED_IN = "SIGNED_IN"
    SIGNED_OUT = "SIGNED_OUT"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"


class Subscription(BaseModel):
    id: str
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
