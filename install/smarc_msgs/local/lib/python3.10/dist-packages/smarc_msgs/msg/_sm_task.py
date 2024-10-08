# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/SMTask.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SMTask(type):
    """Metaclass of message 'SMTask'."""

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
            module = import_type_support('smarc_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_msgs.msg.SMTask')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__sm_task
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__sm_task
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__sm_task
            cls._TYPE_SUPPORT = module.type_support_msg__msg__sm_task
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__sm_task

            from builtin_interfaces.msg import Duration
            if Duration.__class__._TYPE_SUPPORT is None:
                Duration.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class SMTask(metaclass=Metaclass_SMTask):
    """Message class 'SMTask'."""

    __slots__ = [
        '_task_id',
        '_x',
        '_y',
        '_depth',
        '_altitude',
        '_theta',
        '_max_duration',
        '_action_topic',
        '_action_arguments',
    ]

    _fields_and_field_types = {
        'task_id': 'uint64',
        'x': 'double',
        'y': 'double',
        'depth': 'double',
        'altitude': 'double',
        'theta': 'double',
        'max_duration': 'builtin_interfaces/Duration',
        'action_topic': 'string',
        'action_arguments': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Duration'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.task_id = kwargs.get('task_id', int())
        self.x = kwargs.get('x', float())
        self.y = kwargs.get('y', float())
        self.depth = kwargs.get('depth', float())
        self.altitude = kwargs.get('altitude', float())
        self.theta = kwargs.get('theta', float())
        from builtin_interfaces.msg import Duration
        self.max_duration = kwargs.get('max_duration', Duration())
        self.action_topic = kwargs.get('action_topic', str())
        self.action_arguments = kwargs.get('action_arguments', str())

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
        if self.task_id != other.task_id:
            return False
        if self.x != other.x:
            return False
        if self.y != other.y:
            return False
        if self.depth != other.depth:
            return False
        if self.altitude != other.altitude:
            return False
        if self.theta != other.theta:
            return False
        if self.max_duration != other.max_duration:
            return False
        if self.action_topic != other.action_topic:
            return False
        if self.action_arguments != other.action_arguments:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def task_id(self):
        """Message field 'task_id'."""
        return self._task_id

    @task_id.setter
    def task_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'task_id' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'task_id' field must be an unsigned integer in [0, 18446744073709551615]"
        self._task_id = value

    @builtins.property
    def x(self):
        """Message field 'x'."""
        return self._x

    @x.setter
    def x(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'x' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'x' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._x = value

    @builtins.property
    def y(self):
        """Message field 'y'."""
        return self._y

    @y.setter
    def y(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'y' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'y' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._y = value

    @builtins.property
    def depth(self):
        """Message field 'depth'."""
        return self._depth

    @depth.setter
    def depth(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'depth' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'depth' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._depth = value

    @builtins.property
    def altitude(self):
        """Message field 'altitude'."""
        return self._altitude

    @altitude.setter
    def altitude(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'altitude' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'altitude' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._altitude = value

    @builtins.property
    def theta(self):
        """Message field 'theta'."""
        return self._theta

    @theta.setter
    def theta(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'theta' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'theta' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._theta = value

    @builtins.property
    def max_duration(self):
        """Message field 'max_duration'."""
        return self._max_duration

    @max_duration.setter
    def max_duration(self, value):
        if __debug__:
            from builtin_interfaces.msg import Duration
            assert \
                isinstance(value, Duration), \
                "The 'max_duration' field must be a sub message of type 'Duration'"
        self._max_duration = value

    @builtins.property
    def action_topic(self):
        """Message field 'action_topic'."""
        return self._action_topic

    @action_topic.setter
    def action_topic(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'action_topic' field must be of type 'str'"
        self._action_topic = value

    @builtins.property
    def action_arguments(self):
        """Message field 'action_arguments'."""
        return self._action_arguments

    @action_arguments.setter
    def action_arguments(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'action_arguments' field must be of type 'str'"
        self._action_arguments = value
