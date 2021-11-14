from __future__ import annotations

from dataclasses import asdict, dataclass
from inspect import signature
from typing import Any, Dict


@dataclass
class APIError(BaseException):
    msg: str
    code: int

    def __post_init__(self) -> None:
        self.msg = str(self.msg)
        self.code = int(str(self.code))

    @classmethod
    def parse_dict(cls, **json: dict) -> APIError:
        cls_fields = {field for field in signature(cls).parameters}
        native_args, new_args = {}, {}
        for name, val in json.items():
            if name in cls_fields:
                native_args[name] = val
            else:
                new_args[name] = val
        ret = cls(**native_args)
        for new_name, new_val in new_args.items():
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
        return cls.parse_dict(**data)

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
