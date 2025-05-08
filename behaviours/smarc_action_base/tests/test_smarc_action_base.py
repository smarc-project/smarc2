import pytest
from smarc_action_base.smarc_action_base import _validate_state, ActionClientState, combine_ns_and_action


def test_invalid_state():
    with pytest.raises(ValueError):
        _validate_state(1)


def test_valid_state():
    assert ActionClientState.ERROR == _validate_state(ActionClientState.ERROR)


@pytest.mark.parametrize("input, expected", [(("/","t"), "/t"), (("/Quad", "test"),"/Quad/test") ])
def test_namespace(input ,expected):
    output = combine_ns_and_action(input[0], input[1])
    assert(output == expected)

