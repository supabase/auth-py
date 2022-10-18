from __future__ import annotations

from datetime import datetime
from time import time
from typing import Any, Callable, Dict, List, Literal, Union

from pydantic import BaseModel, root_validator
from typing_extensions import NotRequired, TypedDict

Provider = Literal[
    "apple",
    "azure",
    "bitbucket",
    "discord",
    "facebook",
    "github",
    "gitlab",
    "google",
    "keycloak",
    "linkedin",
    "notion",
    "slack",
    "spotify",
    "twitch",
    "twitter",
    "workos",
]

AuthChangeEvent = Literal[
    "PASSWORD_RECOVERY",
    "SIGNED_IN",
    "SIGNED_OUT",
    "TOKEN_REFRESHED",
    "USER_UPDATED",
    "USER_DELETED",
]


class Options(TypedDict, total=False):
    redirect_to: str
    data: Any


class AuthResponse(BaseModel):
    user: Union[User, None] = None
    session: Union[Session, None] = None


class OAuthResponse(BaseModel):
    provider: Provider
    url: str


class UserResponse(BaseModel):
    user: User


class Session(BaseModel):
    provider_token: Union[str, None] = None
    """
    The oauth provider token. If present, this can be used to make external API
    requests to the oauth provider used.
    """
    provider_refresh_token: Union[str, None] = None
    """
    The oauth provider refresh token. If present, this can be used to refresh
    the provider_token via the oauth provider's API.

    Not all oauth providers return a provider refresh token. If the
    provider_refresh_token is missing, please refer to the oauth provider's
    documentation for information on how to obtain the provider refresh token.
    """
    access_token: str
    refresh_token: str
    expires_in: int
    """
    The number of seconds until the token expires (since it was issued).
    Returned when a login is confirmed.
    """
    expires_at: Union[int, None] = None
    """
    A timestamp of when the token will expire. Returned when a login is confirmed.
    """
    token_type: str
    user: User

    @root_validator
    def validator(cls, values: dict) -> dict:
        expires_in = values.get("expires_in")
        if expires_in and not values.get("expires_at"):
            values["expires_at"] = round(time()) + expires_in
        return values


class UserIdentity(BaseModel):
    id: str
    user_id: str
    identity_data: Dict[str, Any]
    provider: str
    created_at: datetime
    last_sign_in_at: datetime
    updated_at: Union[datetime, None] = None


class User(BaseModel):
    id: str
    app_metadata: Dict[str, Any]
    user_metadata: Dict[str, Any]
    aud: str
    confirmation_sent_at: Union[datetime, None] = None
    recovery_sent_at: Union[datetime, None] = None
    email_change_sent_at: Union[datetime, None] = None
    new_email: Union[str, None] = None
    invited_at: Union[datetime, None] = None
    action_link: Union[str, None] = None
    email: Union[str, None] = None
    phone: Union[str, None] = None
    created_at: datetime
    confirmed_at: Union[datetime, None] = None
    email_confirmed_at: Union[datetime, None] = None
    phone_confirmed_at: Union[datetime, None] = None
    last_sign_in_at: Union[datetime, None] = None
    role: Union[str, None] = None
    updated_at: Union[datetime, None] = None
    identities: Union[List[UserIdentity], None] = None


class UserAttributes(TypedDict, total=False):
    email: str
    phone: str
    password: str
    data: Any


class AdminUserAttributes(UserAttributes, TypedDict, total=False):
    user_metadata: Any
    app_metadata: Any
    email_confirm: bool
    phone_confirm: bool
    ban_duration: Union[str, Literal["none"]]


class Subscription(BaseModel):
    id: str
    """
    The subscriber UUID. This will be set by the client.
    """
    callback: Callable[[AuthChangeEvent, Union[Session, None]], None]
    """
    The function to call every time there is an event.
    """
    unsubscribe: Callable[[], None]
    """
    Call this to remove the listener.
    """


class SignUpWithEmailAndPasswordCredentialsOptions(TypedDict, total=False):
    email_redirect_to: str
    data: Any
    captcha_token: str


class SignUpWithEmailAndPasswordCredentials(TypedDict):
    email: str
    password: str
    options: NotRequired[SignUpWithEmailAndPasswordCredentialsOptions]


class SignUpWithPhoneAndPasswordCredentialsOptions(TypedDict, total=False):
    data: Any
    captcha_token: str


class SignUpWithPhoneAndPasswordCredentials(TypedDict):
    phone: str
    password: str
    options: NotRequired[SignUpWithPhoneAndPasswordCredentialsOptions]


SignUpWithPasswordCredentials = Union[
    SignUpWithEmailAndPasswordCredentials,
    SignUpWithPhoneAndPasswordCredentials,
]


class SignInWithPasswordCredentialsOptions(TypedDict, total=False):
    captcha_token: str


class SignInWithEmailAndPasswordCredentials(TypedDict):
    email: str
    password: str
    options: NotRequired[SignInWithPasswordCredentialsOptions]


class SignInWithPhoneAndPasswordCredentials(TypedDict):
    phone: str
    password: str
    options: NotRequired[SignInWithPasswordCredentialsOptions]


SignInWithPasswordCredentials = Union[
    SignInWithEmailAndPasswordCredentials,
    SignInWithPhoneAndPasswordCredentials,
]


class SignInWithEmailAndPasswordlessCredentialsOptions(TypedDict, total=False):
    email_redirect_to: str
    should_create_user: bool
    data: Any
    captcha_token: str


class SignInWithEmailAndPasswordlessCredentials(TypedDict):
    email: str
    options: NotRequired[SignInWithEmailAndPasswordlessCredentialsOptions]


class SignInWithPhoneAndPasswordlessCredentialsOptions(TypedDict, total=False):
    should_create_user: bool
    data: Any
    captcha_token: str


class SignInWithPhoneAndPasswordlessCredentials(TypedDict):
    phone: str
    options: NotRequired[SignInWithPhoneAndPasswordlessCredentialsOptions]


SignInWithPasswordlessCredentials = Union[
    SignInWithEmailAndPasswordlessCredentials,
    SignInWithPhoneAndPasswordlessCredentials,
]


class SignInWithOAuthCredentialsOptions(TypedDict, total=False):
    redirect_to: str
    scopes: str
    query_params: Dict[str, str]


class SignInWithOAuthCredentials(TypedDict):
    provider: Provider
    options: NotRequired[SignInWithOAuthCredentialsOptions]


class VerifyOtpParamsOptions(TypedDict, total=False):
    redirect_to: str
    captcha_token: str


class VerifyEmailOtpParams(TypedDict):
    email: str
    token: str
    type: Literal[
        "signup",
        "invite",
        "magiclink",
        "recovery",
        "email_change",
    ]
    options: NotRequired[VerifyOtpParamsOptions]


class VerifyMobileOtpParams(TypedDict):
    phone: str
    token: str
    type: Literal[
        "sms",
        "phone_change",
    ]
    options: NotRequired[VerifyOtpParamsOptions]


VerifyOtpParams = Union[
    VerifyEmailOtpParams,
    VerifyMobileOtpParams,
]


class GenerateLinkParamsOptions(TypedDict, total=False):
    redirect_to: str


class GenerateLinkParamsWithDataOptions(
    GenerateLinkParamsOptions,
    TypedDict,
    total=False,
):
    data: Any


class GenerateSignupLinkParams(TypedDict):
    type: Literal["signup"]
    email: str
    password: str
    options: NotRequired[GenerateLinkParamsWithDataOptions]


class GenerateInviteOrMagiclinkParams(TypedDict):
    type: Literal["invite", "magiclink"]
    email: str
    options: NotRequired[GenerateLinkParamsWithDataOptions]


class GenerateRecoveryLinkParams(TypedDict):
    type: Literal["recovery"]
    email: str
    options: NotRequired[GenerateLinkParamsOptions]


class GenerateEmailChangeLinkParams(TypedDict):
    type: Literal["email_change"]
    email: str
    new_email: str
    options: NotRequired[GenerateLinkParamsOptions]


GenerateLinkParams = Union[
    GenerateSignupLinkParams,
    GenerateInviteOrMagiclinkParams,
    GenerateRecoveryLinkParams,
    GenerateEmailChangeLinkParams,
]

GenerateLinkType = Literal[
    "signup",
    "invite",
    "magiclink",
    "recovery",
    "email_change_current",
    "email_change_new",
]


class GenerateLinkProperties(BaseModel):
    """
    The properties related to the email link generated.
    """

    action_link: str
    """
    The email link to send to the user. The action_link follows the following format:

    auth/v1/verify?type={verification_type}&token={hashed_token}&redirect_to={redirect_to}
    """
    email_otp: str
    """
    The raw email OTP.
    You should send this in the email if you want your users to verify using an
    OTP instead of the action link.
    """
    hashed_token: str
    """
    The hashed token appended to the action link.
    """
    redirect_to: str
    """
    The URL appended to the action link.
    """
    verification_type: GenerateLinkType
    """
    The verification type that the email link is associated to.
    """


class GenerateLinkResponse(BaseModel):
    properties: GenerateLinkProperties
    user: User
