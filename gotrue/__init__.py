__version__ = "0.2.0"

from ._async.api import AsyncGoTrueApi  # noqa: F401
from ._async.client import AsyncGoTrueClient  # noqa: F401
from ._async.storage import AsyncMemoryStorage, AsyncSupportedStorage  # noqa: F401
from ._sync.api import SyncGoTrueApi  # noqa: F401
from ._sync.client import SyncGoTrueClient  # noqa: F401
from ._sync.storage import SyncMemoryStorage, SyncSupportedStorage  # noqa: F401
from .types import *  # noqa: F401, F403

Client = SyncGoTrueClient
GoTrueApi = SyncGoTrueApi
