import pytest

from sam_diving_controller.controllers.DiveControllerONNX import DiveControllerONNX
from unittest.mock import Mock

sut: DiveControllerONNX


@pytest.fixture(autouse=True)
def test_before_after():
    # Code that will run before your test
    global sut

    node = Mock()
    dive_pub = Mock()
    dive_sub = Mock()

    sut = DiveControllerONNX(node, dive_pub, dive_sub, None, None)

    yield  # A test function will be run at this point

def test_sth():
    assert True