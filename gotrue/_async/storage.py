from abc import ABC, abstractmethod
from typing import Dict, Optional


class AsyncSupportedStorage(ABC):
    @abstractmethod
    async def get_item(self, key: str) -> Optional[str]:
        ...

    @abstractmethod
    async def set_item(self, key: str, value: str) -> None:
        ...

    @abstractmethod
    async def remove_item(self, key: str) -> None:
        ...


class AsyncMemoryStorage(AsyncSupportedStorage):
    def __init__(self):
        self.storage: Dict[str, str] = {}

    async def get_item(self, key: str) -> Optional[str]:
        return self.storage.get(key)

    async def set_item(self, key: str, value: str) -> None:
        self.storage[key] = value

    async def remove_item(self, key: str) -> None:
        del self.storage[key]
