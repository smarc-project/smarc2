import pytest
from smarc_action_base.smarc_action_base import _validate_state, ActionClientState






def test_invalid_state():
    with pytest.raises(ValueError):
        _validate_state(1)

def test_valid_state():
    assert(ActionClientState.ERROR == _validate_state(ActionClientState.ERROR))

