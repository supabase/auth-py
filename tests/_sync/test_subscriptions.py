import pytest

from gotrue import SyncGoTrueClient

client = SyncGoTrueClient()

subscription = client.on_auth_state_change(lambda _, __: print("Auth state changed"))


def test_subscribe_a_listener():
    try:
        assert len(client.state_change_emitters)
    except Exception as e:
        assert False, str(e)


@pytest.mark.depends(on=[test_subscribe_a_listener.__name__])
def test_unsubscribe_a_listener():
    try:
        subscription.unsubscribe()
        assert not len(client.state_change_emitters)
    except Exception as e:
        assert False, str(e)
