from datetime import datetime

import httpx
import pytest
import respx
from httpx import Headers, Response

from supabase_auth.constants import API_VERSION_HEADER_NAME
from supabase_auth.errors import AuthApiError, AuthWeakPasswordError
from supabase_auth.helpers import parse_response_api_version

TEST_URL = f"http://localhost"


def test_handle_exception_with_api_version_and_error_code():
    err = {
        "name": "without API version and error code",
        "code": "error_code",
        "ename": "AuthApiError",
    }

    with respx.mock:
        respx.get(f"{TEST_URL}/hello-world").mock(
            return_value=Response(status_code=200),
            side_effect=AuthApiError("Error code message", 400, "error_code"),
        )
        with pytest.raises(AuthApiError, match=r"Error code message") as exc:
            httpx.get(f"{TEST_URL}/hello-world")
        assert exc.value != None
        assert exc.value.message == "Error code message"
        assert exc.value.code == err["code"]
        assert exc.value.name == err["ename"]


def test_handle_exception_without_api_version_and_weak_password_error_code():
    err = {
        "name": "without API version and weak password error code with payload",
        "code": "weak_password",
        "ename": "AuthWeakPasswordError",
    }

    with respx.mock:
        respx.get(f"{TEST_URL}/hello-world").mock(
            return_value=Response(status_code=200),
            side_effect=AuthWeakPasswordError(
                "Error code message", 400, ["characters"]
            ),
        )
        with pytest.raises(AuthWeakPasswordError, match=r"Error code message") as exc:
            httpx.get(f"{TEST_URL}/hello-world")
        assert exc.value != None
        assert exc.value.message == "Error code message"
        assert exc.value.code == err["code"]
        assert exc.value.name == err["ename"]


def test_handle_exception_with_api_version_2024_01_01_and_error_code():
    err = {
        "name": "with API version 2024-01-01 and error code",
        "code": "error_code",
        "ename": "AuthApiError",
    }

    with respx.mock:
        respx.get(f"{TEST_URL}/hello-world").mock(
            return_value=Response(status_code=200),
            side_effect=AuthApiError("Error code message", 400, "error_code"),
        )
        with pytest.raises(AuthApiError, match=r"Error code message") as exc:
            httpx.get(f"{TEST_URL}/hello-world")
        assert exc.value != None
        assert exc.value.message == "Error code message"
        assert exc.value.code == err["code"]
        assert exc.value.name == err["ename"]


def test_parse_response_api_version_with_valid_date():
    headers = Headers({API_VERSION_HEADER_NAME: "2024-01-01"})
    response = Response(headers=headers, status_code=200)
    api_ver = parse_response_api_version(response)
    assert datetime.timestamp(api_ver) == datetime.timestamp(
        datetime.strptime("2024-01-01", "%Y-%m-%d")
    )


def test_parse_response_api_version_with_invalid_dates():
    dates = ["2024-01-32", "", "notadate", "Sat Feb 24 2024 17:59:17 GMT+0100"]
    for date in dates:
        headers = Headers({API_VERSION_HEADER_NAME: date})
        response = Response(headers=headers, status_code=200)
        api_ver = parse_response_api_version(response)
        assert api_ver == None
