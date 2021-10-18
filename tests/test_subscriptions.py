import pytest

from gotrue import AsyncGoTrueClient

client = AsyncGoTrueClient()

subscription = client.on_auth_state_change(lambda _, __: print("Auth state changed"))


def test_subscribe_a_listener():
    assert len(client.state_change_emitters)


@pytest.mark.depends(on=[test_subscribe_a_listener.__name__])
def test_unsubscribe_a_listener():
    subscription.unsubscribe()
    assert not len(client.state_change_emitters)
