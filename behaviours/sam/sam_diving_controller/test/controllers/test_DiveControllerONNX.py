import pytest
from builtin_interfaces.msg import Time
from geometry_msgs.msg import Point, Quaternion, Vector3
from nav_msgs.msg import Odometry

from sam_diving_controller.controllers.DiveControllerONNX import DiveControllerONNX
from unittest.mock import Mock, patch

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

def test_sth():
    t = Time(sec=123, nanosec=456)
    node.get_clock.return_value.now.return_value.to_msg.return_value = t

    odom = Odometry()
    odom.pose.pose.position = Point(x=1.0, y=2.0, z=3.0)
    odom.pose.pose.orientation = Quaternion(x=0.0, y=0.0, z=0.0, w=1.0)
    odom.twist.twist.linear = Vector3(x=0.1, y=0.2, z=0.3)
    odom.twist.twist.angular = Vector3(x=0.4, y=0.5, z=0.6)

    sut.convert_to_body(odom, odom)

