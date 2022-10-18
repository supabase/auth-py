import pytest

from ...gotrue import AsyncGoTrueClient
from ...gotrue.types import Subscription

GOTRUE_URL = "http://localhost:9999"


@pytest.fixture(name="client")
async def create_client() -> AsyncGoTrueClient:
    async with AsyncGoTrueClient(url=GOTRUE_URL) as client:
        return client


@pytest.fixture(name="subscription")
def create_subscription(client: AsyncGoTrueClient):
    return client.on_auth_state_change(
        callback=lambda _, __: print("Auth state changed")
    )


def test_subscribe_a_listener(client: AsyncGoTrueClient, subscription: Subscription):
    try:
        assert len(client.state_change_emitters)
    except Exception as e:
        assert False, str(e)


@pytest.mark.depends(on=[test_subscribe_a_listener.__name__])
def test_unsubscribe_a_listener(client: AsyncGoTrueClient, subscription: Subscription):
    try:
        subscription.unsubscribe()
        assert not len(client.state_change_emitters)
    except Exception as e:
        assert False, str(e)
