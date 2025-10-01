import pytest

from sam_diving_controller.controllers.DiveControllerONNX import DiveControllerONNX
from unittest.mock import Mock

sut: DiveControllerONNX
node = Mock()
dive_pub = Mock()
dive_sub = Mock()

@pytest.fixture(autouse=True)
def test_before_after():
    # Code that will run before your test
    global sut
    global dive_pub
    global dive_sub
    global node

    node = Mock()
    dive_pub = Mock()
    dive_sub = Mock()

    sut = DiveControllerONNX(node, dive_pub, dive_sub, None, None)

    yield  # A test function will be run at this point

def test_set_publishers():
    sut.set_publishers([1000, 0.2, 0.1, 45, 55])

    dive_pub.set_rpm.assert_called_with(1000, 1000)
    dive_pub.set_vbs.assert_called_once_with(45)
    dive_pub.set_lcg.assert_called_once_with(55)
    dive_pub.set_thrust_vector.assert_called_once_with(0.1, 0.2)

