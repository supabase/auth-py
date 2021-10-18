from dataclasses import dataclass
from enum import Enum
from json import dumps
from typing import Any, Callable, Dict, Optional, TypeVar

T = TypeVar("T")


def parse_none(
    value: Optional[T],
    func: Callable[[Any], T],
) -> Optional[T]:
    if value is None:
        return None
    return func(value)


@dataclass
class ApiError(BaseException):
    message: str
    status: int

    def __post_init__(self) -> None:
        self.message = str(self.message)
        self.status = int(str(self.status))

    @staticmethod
    def from_dict(data: dict) -> "ApiError":
        return ApiError(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "status": self.status,
        }

    def __str__(self) -> str:
        return dumps(self.to_dict())

    def __repr__(self) -> str:
        return self.__str__()


@dataclass
class CookieOptions:
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

    def __post_init__(self) -> None:
        self.name = str(self.name)
        self.lifetime = int(str(self.lifetime))
        self.domain = str(self.domain)
        self.path = str(self.path)
        self.same_site = str(self.same_site)

    @staticmethod
    def from_dict(data: dict) -> "CookieOptions":
        return CookieOptions(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "lifetime": self.lifetime,
            "domain": self.domain,
            "path": self.path,
            "same_site": self.same_site,
        }


@dataclass
class User:
    app_metadata: Dict[str, Any]
    aud: str
    created_at: str
    email_change_confirm_status: bool
    id: str
    user_metadata: Optional[Dict[str, Any]] = None
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

    def __post_init__(self) -> None:
        self.action_link = parse_none(self.action_link, str)
        self.app_metadata = dict(self.app_metadata)
        self.aud = str(self.aud)
        self.confirmation_sent_at = parse_none(self.confirmation_sent_at, str)
        self.confirmed_at = parse_none(self.confirmed_at, str)
        self.created_at = str(self.created_at)
        self.email = parse_none(self.email, str)
        self.email_confirmed_at = parse_none(self.email_confirmed_at, str)
        self.email_change_confirm_status = bool(self.email_change_confirm_status)
        self.id = str(self.id)
        self.last_sign_in_at = parse_none(self.last_sign_in_at, str)
        self.phone = parse_none(self.phone, str)
        self.phone_confirmed_at = parse_none(self.phone_confirmed_at, str)
        self.recovery_sent_at = parse_none(self.recovery_sent_at, str)
        self.role = parse_none(self.role, str)
        self.updated_at = parse_none(self.updated_at, str)
        self.user_metadata = parse_none(self.user_metadata, dict)
        self.invited_at = parse_none(self.invited_at, str)

    @staticmethod
    def from_dict(data: dict) -> "User":
        return User(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "action_link": self.action_link,
            "app_metadata": self.app_metadata,
            "aud": self.aud,
            "confirmation_sent_at": self.confirmation_sent_at,
            "confirmed_at": self.confirmed_at,
            "created_at": self.created_at,
            "email": self.email,
            "email_confirmed_at": self.email_confirmed_at,
            "email_change_confirm_status": self.email_change_confirm_status,
            "id": self.id,
            "last_sign_in_at": self.last_sign_in_at,
            "phone": self.phone,
            "phone_confirmed_at": self.phone_confirmed_at,
            "recovery_sent_at": self.recovery_sent_at,
            "role": self.role,
            "updated_at": self.updated_at,
            "user_metadata": self.user_metadata,
            "invited_at": self.invited_at,
        }


@dataclass
class UserAttributes:
    email: Optional[str] = None
    """The user's email."""
    password: Optional[str] = None
    """The user's password."""
    email_change_token: Optional[str] = None
    """An email change token."""
    data: Optional[Any] = None
    """A custom data object. Can be any JSON."""

    def __post_init__(self) -> None:
        self.email = parse_none(self.email, str)
        self.password = parse_none(self.password, str)
        self.email_change_token = parse_none(self.email_change_token, str)
        self.data = parse_none(self.data, Any)

    @staticmethod
    def from_dict(data: dict) -> "UserAttributes":
        return UserAttributes(**data)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "email": self.email,
            "password": self.password,
            "email_change_token": self.email_change_token,
            "data": self.data,
        }


@dataclass
class Session:
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

    def __post_init__(self) -> None:
        self.access_token = str(self.access_token)
        self.expires_at = parse_none(self.expires_at, lambda x: int(str(x)))
        self.expires_in = parse_none(self.expires_in, lambda x: int(str(x)))
        self.provider_token = parse_none(self.provider_token, str)
        self.refresh_token = parse_none(self.refresh_token, str)
        self.token_type = str(self.token_type)
        if self.user:
            self.user.__post_init__()

    @staticmethod
    def from_dict(data: dict) -> "Session":
        user: Optional[User] = None
        user_data = data.get("user")
        if user_data:
            user = User.from_dict(user_data)
        del data["user"]
        return Session(**data, user=user)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "access_token": self.access_token,
            "expires_at": self.expires_at,
            "expires_in": self.expires_in,
            "provider_token": self.provider_token,
            "refresh_token": self.refresh_token,
            "token_type": self.token_type,
        }
        if self.user:
            data["user"] = self.user.to_dict()
        return data


@dataclass
class Subscription:
    id: str
    """The subscriber UUID. This will be set by the client."""
    callback: Callable[["AuthChangeEvent", Optional[Session]], None]
    """The function to call every time there is an event."""
    unsubscribe: Callable[[], None]
    """Call this to remove the listener."""

    def __post_init__(self) -> None:
        self.id = str(self.id)


class AuthChangeEvent(str, Enum):
    SIGNED_IN = "SIGNED_IN"
    SIGNED_OUT = "SIGNED_OUT"
    USER_UPDATED = "USER_UPDATED"
    USER_DELETED = "USER_DELETED"
    PASSWORD_RECOVERY = "PASSWORD_RECOVERY"


class Provider(str, Enum):
    azure = "azure"
    bitbucket = "bitbucket"
    facebook = "facebook"
    github = "github"
    gitlab = "gitlab"
    google = "google"
    twitter = "twitter"
    apple = "apple"
    discord = "discord"
    twitch = "twitch"


class LinkType(str, Enum):
    """The type of link."""

    signup = "signup"
    magiclink = "magiclink"
    recovery = "recovery"
    invite = "invite"
