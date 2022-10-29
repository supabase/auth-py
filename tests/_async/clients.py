from gotrue import AsyncGoTrueAdminAPI, AsyncGoTrueClient
from jwt import encode

SIGNUP_ENABLED_AUTO_CONFIRM_OFF_PORT = 9999
SIGNUP_ENABLED_AUTO_CONFIRM_ON_PORT = 9998
SIGNUP_DISABLED_AUTO_CONFIRM_OFF_PORT = 9997

GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_OFF = (
    f"http://localhost:{SIGNUP_ENABLED_AUTO_CONFIRM_OFF_PORT}"
)
GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON = (
    f"http://localhost:{SIGNUP_ENABLED_AUTO_CONFIRM_ON_PORT}"
)
GOTRUE_URL_SIGNUP_DISABLED_AUTO_CONFIRM_OFF = (
    f"http://localhost:{SIGNUP_DISABLED_AUTO_CONFIRM_OFF_PORT}"
)

GOTRUE_JWT_SECRET = "37c304f8-51aa-419a-a1af-06154e63707a"

AUTH_ADMIN_JWT = encode(
    {
        "sub": "1234567890",
        "role": "supabase_admin",
    },
    GOTRUE_JWT_SECRET,
)

auth_client = AsyncGoTrueClient(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON,
    auto_refresh_token=False,
    persist_session=True,
)

auth_client_with_session = AsyncGoTrueClient(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON,
    auto_refresh_token=False,
    persist_session=False,
)

auth_subscription_client = AsyncGoTrueClient(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON,
    auto_refresh_token=False,
    persist_session=True,
)


client_api_auto_confirm_enabled_client = AsyncGoTrueClient(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON,
    auto_refresh_token=False,
    persist_session=True,
)

client_api_auto_confirm_off_signups_enabled_client = AsyncGoTrueClient(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_OFF,
    auto_refresh_token=False,
    persist_session=True,
)

client_api_auto_confirm_disabled_client = AsyncGoTrueClient(
    url=GOTRUE_URL_SIGNUP_DISABLED_AUTO_CONFIRM_OFF,
    auto_refresh_token=False,
    persist_session=True,
)

auth_admin_api_auto_confirm_enabled_client = AsyncGoTrueAdminAPI(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON,
    headers={
        "Authorization": f"Bearer {AUTH_ADMIN_JWT}",
    },
)

auth_admin_api_auto_confirm_disabled_client = AsyncGoTrueAdminAPI(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_OFF,
    headers={
        "Authorization": f"Bearer {AUTH_ADMIN_JWT}",
    },
)

SERVICE_ROLE_JWT = encode(
    {
        "role": "service_role",
    },
    GOTRUE_JWT_SECRET,
)

service_role_api_client = AsyncGoTrueAdminAPI(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_ON,
    headers={
        "Authorization": f"Bearer {SERVICE_ROLE_JWT}",
    },
)

service_role_api_client_with_sms = AsyncGoTrueAdminAPI(
    url=GOTRUE_URL_SIGNUP_ENABLED_AUTO_CONFIRM_OFF,
    headers={
        "Authorization": f"Bearer {SERVICE_ROLE_JWT}",
    },
)

service_role_api_client_no_sms = AsyncGoTrueAdminAPI(
    url=GOTRUE_URL_SIGNUP_DISABLED_AUTO_CONFIRM_OFF,
    headers={
        "Authorization": f"Bearer {SERVICE_ROLE_JWT}",
    },
)
