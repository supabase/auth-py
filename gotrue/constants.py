from __future__ import annotations

from gotrue import __version__

GOTRUE_URL = "http://localhost:9999"
AUDIENCE = ""
DEFAULT_HEADERS = {
    "X-Client-Info": f"gotrue-py/{__version__}",
}
EXPIRY_MARGIN = 60 * 1000
STORAGE_KEY = "supabase.auth.token"
COOKIE_OPTIONS = {
    "name": "sb:token",
    "lifetime": 60 * 60 * 8,
    "domain": "",
    "path": "/",
    "same_site": "lax",
}
