from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict


@dataclass
class APIError(Exception):
    msg: str
    code: int

    def __post_init__(self) -> None:
        self.msg = str(self.msg)
        self.code = int(str(self.code))

    @classmethod
    def parse_dict(cls, **json: dict) -> APIError:
        ret = cls(msg="Unknown error", code=-1)
        for new_name, new_val in json.items():
            setattr(ret, new_name, new_val)
        return ret

    @classmethod
    def from_dict(cls, data: dict) -> APIError:
        if "msg" in data and "code" in data:
            return APIError(
                msg=data["msg"],
                code=data["code"],
            )
        if "error" in data and "error_description" in data:
            try:
                code = int(data["error"])
            except ValueError:
                code = -1
            return APIError(
                msg=data["error_description"],
                code=code,
            )
        if "message" in data:
            try:
                code = int(data.get("code", -1))
            except ValueError:
                code = -1
            return APIError(
                msg=data["message"],
                code=code,
            )
        return cls.parse_dict(**data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
