from __future__ import annotations

__version__ = "0.5.4"

from ._async.client import AsyncGoTrueClient
from ._async.gotrue_admin_api import AsyncGoTrueAdminAPI
from ._async.storage import AsyncMemoryStorage, AsyncSupportedStorage
from ._sync.client import SyncGoTrueClient
from ._sync.gotrue_admin_api import SyncGoTrueAdminAPI
from ._sync.storage import SyncMemoryStorage, SyncSupportedStorage
from .types import *

Client = SyncGoTrueClient
GoTrueAPI = SyncGoTrueAdminAPI
