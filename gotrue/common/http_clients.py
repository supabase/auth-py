from httpx import AsyncClient  # noqa: F401
from httpx import Client as BaseClient  # noqa: F401


class SyncClient(BaseClient):
    def aclose(self) -> None:
        self.close()
