from __future__ import annotations

from urllib.parse import quote

from httpx import HTTPError, Response

from .exceptions import APIError


def encode_uri_component(uri: str) -> str:
    return quote(uri.encode("utf-8"))


def check_response(response: Response) -> None:
    try:
        response.raise_for_status()
    except HTTPError:
        raise APIError.from_dict(response.json())
