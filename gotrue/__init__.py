from __future__ import annotations

__version__ = "0.5.4"

from ._async.api import AsyncGoTrueAPI
from ._async.client import AsyncGoTrueClient
from ._async.storage import AsyncMemoryStorage, AsyncSupportedStorage
from ._sync.api import SyncGoTrueAPI
from ._sync.client import SyncGoTrueClient
from ._sync.storage import SyncMemoryStorage, SyncSupportedStorage
from .types import *

Client = SyncGoTrueClient
GoTrueAPI = SyncGoTrueAPI
