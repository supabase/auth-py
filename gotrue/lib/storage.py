from abc import ABC, abstractmethod
from typing import Dict, Optional


class SupportedStorage(ABC):
    @abstractmethod
    def get_item(self, key: str) -> Optional[str]:
        ...

    @abstractmethod
    def set_item(self, key: str, value: str) -> None:
        ...

    @abstractmethod
    def remove_item(self, key: str) -> None:
        ...


class MemoryStorage(SupportedStorage):
    def __init__(self):
        self.storage: Dict[str, str] = {}

    def get_item(self, key: str) -> Optional[str]:
        return self.storage.get(key)

    def set_item(self, key: str, value: str) -> None:
        self.storage[key] = value

    def remove_item(self, key: str) -> None:
        del self.storage[key]
