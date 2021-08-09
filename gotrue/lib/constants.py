from typing import Dict, Union
GOTRUE_URL: str = 'http://localhost:9999'
AUDIENCE: str = ''
DEFAULT_HEADERS: Dict[str, str] = {}
EXPIRY_MARGIN: int = 60 * 1000
STORAGE_KEY: str = 'supabase.auth.token'
COOKIE_OPTIONS: Dict[str, Union[str, int]] = {
    "name": 'sb:token',
    "lifetime": 60 * 60 * 8,
    "domain": '',
    "path": '/',
    "sameSite": 'lax',
}
