# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:msg/GotoWaypoint.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GotoWaypoint(type):
    """Metaclass of message 'GotoWaypoint'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'Z_CONTROL_NONE': 0,
        'Z_CONTROL_DEPTH': 1,
        'Z_CONTROL_ALTITUDE': 2,
        'SPEED_CONTROL_NONE': 0,
        'SPEED_CONTROL_RPM': 1,
        'SPEED_CONTROL_SPEED': 2,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('smarc_mission_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_mission_msgs.msg.GotoWaypoint')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__goto_waypoint
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__goto_waypoint
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__goto_waypoint
            cls._TYPE_SUPPORT = module.type_support_msg__msg__goto_waypoint
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__goto_waypoint

            from geometry_msgs.msg import PoseStamped
            if PoseStamped.__class__._TYPE_SUPPORT is None:
                PoseStamped.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'Z_CONTROL_NONE': cls.__constants['Z_CONTROL_NONE'],
            'Z_CONTROL_DEPTH': cls.__constants['Z_CONTROL_DEPTH'],
            'Z_CONTROL_ALTITUDE': cls.__constants['Z_CONTROL_ALTITUDE'],
            'SPEED_CONTROL_NONE': cls.__constants['SPEED_CONTROL_NONE'],
            'SPEED_CONTROL_RPM': cls.__constants['SPEED_CONTROL_RPM'],
            'SPEED_CONTROL_SPEED': cls.__constants['SPEED_CONTROL_SPEED'],
        }

    @property
    def Z_CONTROL_NONE(self):
        """Message constant 'Z_CONTROL_NONE'."""
        return Metaclass_GotoWaypoint.__constants['Z_CONTROL_NONE']

    @property
    def Z_CONTROL_DEPTH(self):
        """Message constant 'Z_CONTROL_DEPTH'."""
        return Metaclass_GotoWaypoint.__constants['Z_CONTROL_DEPTH']

    @property
    def Z_CONTROL_ALTITUDE(self):
        """Message constant 'Z_CONTROL_ALTITUDE'."""
        return Metaclass_GotoWaypoint.__constants['Z_CONTROL_ALTITUDE']

    @property
    def SPEED_CONTROL_NONE(self):
        """Message constant 'SPEED_CONTROL_NONE'."""
        return Metaclass_GotoWaypoint.__constants['SPEED_CONTROL_NONE']

    @property
    def SPEED_CONTROL_RPM(self):
        """Message constant 'SPEED_CONTROL_RPM'."""
        return Metaclass_GotoWaypoint.__constants['SPEED_CONTROL_RPM']

    @property
    def SPEED_CONTROL_SPEED(self):
        """Message constant 'SPEED_CONTROL_SPEED'."""
        return Metaclass_GotoWaypoint.__constants['SPEED_CONTROL_SPEED']


class GotoWaypoint(metaclass=Metaclass_GotoWaypoint):
    """
    Message class 'GotoWaypoint'.

    Constants:
      Z_CONTROL_NONE
      Z_CONTROL_DEPTH
      Z_CONTROL_ALTITUDE
      SPEED_CONTROL_NONE
      SPEED_CONTROL_RPM
      SPEED_CONTROL_SPEED
    """

    __slots__ = [
        '_pose',
        '_goal_tolerance',
        '_z_control_mode',
        '_travel_altitude',
        '_travel_depth',
        '_speed_control_mode',
        '_travel_rpm',
        '_travel_speed',
        '_lat',
        '_lon',
        '_arrival_heading',
        '_use_heading',
        '_name',
    ]

    _fields_and_field_types = {
        'pose': 'geometry_msgs/PoseStamped',
        'goal_tolerance': 'double',
        'z_control_mode': 'uint8',
        'travel_altitude': 'double',
        'travel_depth': 'double',
        'speed_control_mode': 'uint8',
        'travel_rpm': 'double',
        'travel_speed': 'double',
        'lat': 'double',
        'lon': 'double',
        'arrival_heading': 'double',
        'use_heading': 'boolean',
        'name': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'PoseStamped'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from geometry_msgs.msg import PoseStamped
        self.pose = kwargs.get('pose', PoseStamped())
        self.goal_tolerance = kwargs.get('goal_tolerance', float())
        self.z_control_mode = kwargs.get('z_control_mode', int())
        self.travel_altitude = kwargs.get('travel_altitude', float())
        self.travel_depth = kwargs.get('travel_depth', float())
        self.speed_control_mode = kwargs.get('speed_control_mode', int())
        self.travel_rpm = kwargs.get('travel_rpm', float())
        self.travel_speed = kwargs.get('travel_speed', float())
        self.lat = kwargs.get('lat', float())
        self.lon = kwargs.get('lon', float())
        self.arrival_heading = kwargs.get('arrival_heading', float())
        self.use_heading = kwargs.get('use_heading', bool())
        self.name = kwargs.get('name', str())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.__slots__, self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s[1:] + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.pose != other.pose:
            return False
        if self.goal_tolerance != other.goal_tolerance:
            return False
        if self.z_control_mode != other.z_control_mode:
            return False
        if self.travel_altitude != other.travel_altitude:
            return False
        if self.travel_depth != other.travel_depth:
            return False
        if self.speed_control_mode != other.speed_control_mode:
            return False
        if self.travel_rpm != other.travel_rpm:
            return False
        if self.travel_speed != other.travel_speed:
            return False
        if self.lat != other.lat:
            return False
        if self.lon != other.lon:
            return False
        if self.arrival_heading != other.arrival_heading:
            return False
        if self.use_heading != other.use_heading:
            return False
        if self.name != other.name:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def pose(self):
        """Message field 'pose'."""
        return self._pose

    @pose.setter
    def pose(self, value):
        if __debug__:
            from geometry_msgs.msg import PoseStamped
            assert \
                isinstance(value, PoseStamped), \
                "The 'pose' field must be a sub message of type 'PoseStamped'"
        self._pose = value

    @builtins.property
    def goal_tolerance(self):
        """Message field 'goal_tolerance'."""
        return self._goal_tolerance

    @goal_tolerance.setter
    def goal_tolerance(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'goal_tolerance' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'goal_tolerance' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._goal_tolerance = value

    @builtins.property
    def z_control_mode(self):
        """Message field 'z_control_mode'."""
        return self._z_control_mode

    @z_control_mode.setter
    def z_control_mode(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'z_control_mode' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'z_control_mode' field must be an unsigned integer in [0, 255]"
        self._z_control_mode = value

    @builtins.property
    def travel_altitude(self):
        """Message field 'travel_altitude'."""
        return self._travel_altitude

    @travel_altitude.setter
    def travel_altitude(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'travel_altitude' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'travel_altitude' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._travel_altitude = value

    @builtins.property
    def travel_depth(self):
        """Message field 'travel_depth'."""
        return self._travel_depth

    @travel_depth.setter
    def travel_depth(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'travel_depth' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'travel_depth' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._travel_depth = value

    @builtins.property
    def speed_control_mode(self):
        """Message field 'speed_control_mode'."""
        return self._speed_control_mode

    @speed_control_mode.setter
    def speed_control_mode(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'speed_control_mode' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'speed_control_mode' field must be an unsigned integer in [0, 255]"
        self._speed_control_mode = value

    @builtins.property
    def travel_rpm(self):
        """Message field 'travel_rpm'."""
        return self._travel_rpm

    @travel_rpm.setter
    def travel_rpm(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'travel_rpm' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'travel_rpm' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._travel_rpm = value

    @builtins.property
    def travel_speed(self):
        """Message field 'travel_speed'."""
        return self._travel_speed

    @travel_speed.setter
    def travel_speed(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'travel_speed' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'travel_speed' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._travel_speed = value

    @builtins.property
    def lat(self):
        """Message field 'lat'."""
        return self._lat

    @lat.setter
    def lat(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'lat' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'lat' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._lat = value

    @builtins.property
    def lon(self):
        """Message field 'lon'."""
        return self._lon

    @lon.setter
    def lon(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'lon' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'lon' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._lon = value

    @builtins.property
    def arrival_heading(self):
        """Message field 'arrival_heading'."""
        return self._arrival_heading

    @arrival_heading.setter
    def arrival_heading(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'arrival_heading' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'arrival_heading' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._arrival_heading = value

    @builtins.property
    def use_heading(self):
        """Message field 'use_heading'."""
        return self._use_heading

    @use_heading.setter
    def use_heading(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'use_heading' field must be of type 'bool'"
        self._use_heading = value

    @builtins.property
    def name(self):
        """Message field 'name'."""
        return self._name

    @name.setter
    def name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'name' field must be of type 'str'"
        self._name = value
