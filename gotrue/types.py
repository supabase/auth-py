from __future__ import annotations

import sys
from datetime import datetime
from enum import Enum
from time import time
from typing import Any, Callable, Dict, List, Optional, Type, TypeVar, Union
from uuid import UUID

if sys.version_info >= (3, 8):
    from typing import Literal, NotRequired, TypedDict
else:
    from typing_extensions import Literal, TypedDict, NotRequired

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
    id: str
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
    factors: Union[List[Factor], None] = None


class Factor(BaseModel):
    """
    A MFA factor.
    """

    id: str
    """
    ID of the factor.
    """
    friendly_name: Union[str, None] = None
    """
    Friendly name of the factor, useful to disambiguate between multiple factors.
    """
    factor_type: Union[Literal["totp"], str]
    """
    Type of factor. Only `totp` supported with this version but may change in
    future versions.
    """
    status: Literal["verified", "unverified"]
    """
    Factor's status.
    """
    created_at: datetime
    updated_at: datetime


class UpdatableFactorAttributes(TypedDict):
    friendly_name: str


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


class UserAttributesDict(TypedDict, total=False):
    """Dict version of `UserAttributes`"""

    email: Optional[str]
    password: Optional[str]
    email_change_token: Optional[str]
    data: Optional[Any]


class MFAEnrollParams(TypedDict):
    factor_type: Literal["totp"]
    issuer: NotRequired[str]
    friendly_name: NotRequired[str]


class MFAUnenrollParams(TypedDict):
    factor_id: str
    """
    ID of the factor being unenrolled.
    """


class MFAVerifyParams(TypedDict):
    factor_id: str
    """
     ID of the factor being verified.
     """
    challenge_id: str
    """
     ID of the challenge being verified.
     """
    code: str
    """
     Verification code provided by the user.
     """


class MFAChallengeParams(TypedDict):
    factor_id: str
    """
    ID of the factor to be challenged.
    """


class MFAChallengeAndVerifyParams(TypedDict):
    factor_id: str
    """
    ID of the factor being verified.
    """
    code: str
    """
    Verification code provided by the user.
    """


class AuthMFAVerifyResponse(BaseModel):
    access_token: str
    """
   New access token (JWT) after successful verification.
   """
    token_type: str
    """
   Type of token, typically `Bearer`.
   """
    expires_in: int
    """
   Number of seconds in which the access token will expire.
   """
    refresh_token: str
    """
   Refresh token you can use to obtain new access tokens when expired.
   """
    user: User
    """
   Updated user profile.
   """


class AuthMFAEnrollResponseTotp(BaseModel):
    qr_code: str
    """
   Contains a QR code encoding the authenticator URI. You can
   convert it to a URL by prepending `data:image/svg+xml;utf-8,` to
   the value. Avoid logging this value to the console.
   """
    secret: str
    """
   The TOTP secret (also encoded in the QR code). Show this secret
   in a password-style field to the user, in case they are unable to
   scan the QR code. Avoid logging this value to the console.
   """
    uri: str
    """
   The authenticator URI encoded within the QR code, should you need
   to use it. Avoid loggin this value to the console.
   """


class AuthMFAEnrollResponse(BaseModel):
    id: str
    """
   ID of the factor that was just enrolled (in an unverified state).
   """
    type: Literal["totp"]
    """
   Type of MFA factor. Only `totp` supported for now.
   """
    totp: AuthMFAEnrollResponseTotp
    """
   TOTP enrollment information.
   """


class AuthMFAUnenrollResponse(BaseModel):
    id: str
    """
   ID of the factor that was successfully unenrolled.
   """


class AuthMFAChallengeResponse(BaseModel):
    id: str
    """
   ID of the newly created challenge.
   """
    expires_at: int
    """
   Timestamp in UNIX seconds when this challenge will no longer be usable.
   """


class AuthMFAListFactorsResponse(BaseModel):
    all: List[Factor]
    """
   All available factors (verified and unverified).
   """
    totp: List[Factor]
    """
   Only verified TOTP factors. (A subset of `all`.)
   """


AuthenticatorAssuranceLevels = Literal["aal1", "aal2"]


class AuthMFAGetAuthenticatorAssuranceLevelResponse(BaseModel):
    current_level: Union[AuthenticatorAssuranceLevels, None] = None
    """
   Current AAL level of the session.
   """
    next_level: Union[AuthenticatorAssuranceLevels, None] = None
    """
   Next possible AAL level for the session. If the next level is higher
   than the current one, the user should go through MFA.
   """
    current_authentication_methods: List[AMREntry]
    """
   A list of all authentication methods attached to this session. Use
   the information here to detect the last time a user verified a
   factor, for example if implementing a step-up scenario.
   """


class AuthMFAAdminDeleteFactorResponse(BaseModel):
    id: str
    """
   ID of the factor that was successfully deleted.
   """


class AuthMFAAdminDeleteFactorParams(TypedDict):
    id: str
    """
   ID of the MFA factor to delete.
   """
    user_id: str
    """
   ID of the user whose factor is being deleted.
   """


class AuthMFAAdminListFactorsResponse(BaseModel):
    factors: List[Factor]
    """
    All factors attached to the user.
    """


class AuthMFAAdminListFactorsParams(TypedDict):
    user_id: str
    """
    ID of the user for which to list all MFA factors.
    """


class DecodedJWTDict(TypedDict):
    exp: NotRequired[int]
    aal: NotRequired[Union[AuthenticatorAssuranceLevels, None]]
    amr: NotRequired[Union[List[AMREntry], None]]


AMREntry.update_forward_refs()
UserResponse.update_forward_refs()
Factor.update_forward_refs()
User.update_forward_refs()
AuthMFAVerifyResponse.update_forward_refs()
AuthMFAEnrollResponseTotp.update_forward_refs()
AuthMFAEnrollResponse.update_forward_refs()
AuthMFAUnenrollResponse.update_forward_refs()
AuthMFAChallengeResponse.update_forward_refs()
AuthMFAListFactorsResponse.update_forward_refs()
AuthMFAGetAuthenticatorAssuranceLevelResponse.update_forward_refs()
AuthMFAAdminDeleteFactorResponse.update_forward_refs()
AuthMFAAdminListFactorsResponse.update_forward_refs()
