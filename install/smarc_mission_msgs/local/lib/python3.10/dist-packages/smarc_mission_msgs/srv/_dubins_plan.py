# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:srv/DubinsPlan.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_DubinsPlan_Request(type):
    """Metaclass of message 'DubinsPlan_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'smarc_mission_msgs.srv.DubinsPlan_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__dubins_plan__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__dubins_plan__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__dubins_plan__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__dubins_plan__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__dubins_plan__request

            from geometry_msgs.msg import Pose2D
            if Pose2D.__class__._TYPE_SUPPORT is None:
                Pose2D.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DubinsPlan_Request(metaclass=Metaclass_DubinsPlan_Request):
    """Message class 'DubinsPlan_Request'."""

    __slots__ = [
        '_waypoints',
        '_step',
        '_turning_radius',
    ]

    _fields_and_field_types = {
        'waypoints': 'sequence<geometry_msgs/Pose2D>',
        'step': 'double',
        'turning_radius': 'double',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Pose2D')),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.waypoints = kwargs.get('waypoints', [])
        self.step = kwargs.get('step', float())
        self.turning_radius = kwargs.get('turning_radius', float())

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
        if self.waypoints != other.waypoints:
            return False
        if self.step != other.step:
            return False
        if self.turning_radius != other.turning_radius:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def waypoints(self):
        """Message field 'waypoints'."""
        return self._waypoints

    @waypoints.setter
    def waypoints(self, value):
        if __debug__:
            from geometry_msgs.msg import Pose2D
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, Pose2D) for v in value) and
                 True), \
                "The 'waypoints' field must be a set or sequence and each value of type 'Pose2D'"
        self._waypoints = value

    @builtins.property
    def step(self):
        """Message field 'step'."""
        return self._step

    @step.setter
    def step(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'step' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'step' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._step = value

    @builtins.property
    def turning_radius(self):
        """Message field 'turning_radius'."""
        return self._turning_radius

    @turning_radius.setter
    def turning_radius(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'turning_radius' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'turning_radius' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._turning_radius = value


# Import statements for member types

# Member 'original_wp_indices'
import array  # noqa: E402, I100

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_DubinsPlan_Response(type):
    """Metaclass of message 'DubinsPlan_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
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
                'smarc_mission_msgs.srv.DubinsPlan_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__dubins_plan__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__dubins_plan__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__dubins_plan__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__dubins_plan__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__dubins_plan__response

            from geometry_msgs.msg import Pose2D
            if Pose2D.__class__._TYPE_SUPPORT is None:
                Pose2D.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DubinsPlan_Response(metaclass=Metaclass_DubinsPlan_Response):
    """Message class 'DubinsPlan_Response'."""

    __slots__ = [
        '_waypoints',
        '_original_wp_indices',
    ]

    _fields_and_field_types = {
        'waypoints': 'sequence<geometry_msgs/Pose2D>',
        'original_wp_indices': 'sequence<uint16>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'Pose2D')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint16')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.waypoints = kwargs.get('waypoints', [])
        self.original_wp_indices = array.array('H', kwargs.get('original_wp_indices', []))

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
        if self.waypoints != other.waypoints:
            return False
        if self.original_wp_indices != other.original_wp_indices:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def waypoints(self):
        """Message field 'waypoints'."""
        return self._waypoints

    @waypoints.setter
    def waypoints(self, value):
        if __debug__:
            from geometry_msgs.msg import Pose2D
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, Pose2D) for v in value) and
                 True), \
                "The 'waypoints' field must be a set or sequence and each value of type 'Pose2D'"
        self._waypoints = value

    @builtins.property
    def original_wp_indices(self):
        """Message field 'original_wp_indices'."""
        return self._original_wp_indices

    @original_wp_indices.setter
    def original_wp_indices(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'H', \
                "The 'original_wp_indices' array.array() must have the type code of 'H'"
            self._original_wp_indices = value
            return
        if __debug__:
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, int) for v in value) and
                 all(val >= 0 and val < 65536 for val in value)), \
                "The 'original_wp_indices' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 65535]"
        self._original_wp_indices = array.array('H', value)


class Metaclass_DubinsPlan(type):
    """Metaclass of service 'DubinsPlan'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('smarc_mission_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_mission_msgs.srv.DubinsPlan')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__dubins_plan

            from smarc_mission_msgs.srv import _dubins_plan
            if _dubins_plan.Metaclass_DubinsPlan_Request._TYPE_SUPPORT is None:
                _dubins_plan.Metaclass_DubinsPlan_Request.__import_type_support__()
            if _dubins_plan.Metaclass_DubinsPlan_Response._TYPE_SUPPORT is None:
                _dubins_plan.Metaclass_DubinsPlan_Response.__import_type_support__()


class DubinsPlan(metaclass=Metaclass_DubinsPlan):
    from smarc_mission_msgs.srv._dubins_plan import DubinsPlan_Request as Request
    from smarc_mission_msgs.srv._dubins_plan import DubinsPlan_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
