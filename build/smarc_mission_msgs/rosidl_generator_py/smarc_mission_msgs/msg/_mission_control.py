# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:msg/MissionControl.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_MissionControl(type):
    """Metaclass of message 'MissionControl'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'CMD_START': 0,
        'CMD_STOP': 1,
        'CMD_PAUSE': 2,
        'CMD_EMERGENCY': 3,
        'CMD_SET_PLAN': 4,
        'CMD_IS_FEEDBACK': 5,
        'CMD_REQUEST_FEEDBACK': 6,
        'FB_RUNNING': 0,
        'FB_STOPPED': 1,
        'FB_PAUSED': 2,
        'FB_EMERGENCY': 3,
        'FB_RECEIVED': 4,
        'FB_COMPLETED': 5,
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
                'smarc_mission_msgs.msg.MissionControl')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__mission_control
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__mission_control
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__mission_control
            cls._TYPE_SUPPORT = module.type_support_msg__msg__mission_control
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__mission_control

            from smarc_mission_msgs.msg import GotoWaypoint
            if GotoWaypoint.__class__._TYPE_SUPPORT is None:
                GotoWaypoint.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'CMD_START': cls.__constants['CMD_START'],
            'CMD_STOP': cls.__constants['CMD_STOP'],
            'CMD_PAUSE': cls.__constants['CMD_PAUSE'],
            'CMD_EMERGENCY': cls.__constants['CMD_EMERGENCY'],
            'CMD_SET_PLAN': cls.__constants['CMD_SET_PLAN'],
            'CMD_IS_FEEDBACK': cls.__constants['CMD_IS_FEEDBACK'],
            'CMD_REQUEST_FEEDBACK': cls.__constants['CMD_REQUEST_FEEDBACK'],
            'FB_RUNNING': cls.__constants['FB_RUNNING'],
            'FB_STOPPED': cls.__constants['FB_STOPPED'],
            'FB_PAUSED': cls.__constants['FB_PAUSED'],
            'FB_EMERGENCY': cls.__constants['FB_EMERGENCY'],
            'FB_RECEIVED': cls.__constants['FB_RECEIVED'],
            'FB_COMPLETED': cls.__constants['FB_COMPLETED'],
        }

    @property
    def CMD_START(self):
        """Message constant 'CMD_START'."""
        return Metaclass_MissionControl.__constants['CMD_START']

    @property
    def CMD_STOP(self):
        """Message constant 'CMD_STOP'."""
        return Metaclass_MissionControl.__constants['CMD_STOP']

    @property
    def CMD_PAUSE(self):
        """Message constant 'CMD_PAUSE'."""
        return Metaclass_MissionControl.__constants['CMD_PAUSE']

    @property
    def CMD_EMERGENCY(self):
        """Message constant 'CMD_EMERGENCY'."""
        return Metaclass_MissionControl.__constants['CMD_EMERGENCY']

    @property
    def CMD_SET_PLAN(self):
        """Message constant 'CMD_SET_PLAN'."""
        return Metaclass_MissionControl.__constants['CMD_SET_PLAN']

    @property
    def CMD_IS_FEEDBACK(self):
        """Message constant 'CMD_IS_FEEDBACK'."""
        return Metaclass_MissionControl.__constants['CMD_IS_FEEDBACK']

    @property
    def CMD_REQUEST_FEEDBACK(self):
        """Message constant 'CMD_REQUEST_FEEDBACK'."""
        return Metaclass_MissionControl.__constants['CMD_REQUEST_FEEDBACK']

    @property
    def FB_RUNNING(self):
        """Message constant 'FB_RUNNING'."""
        return Metaclass_MissionControl.__constants['FB_RUNNING']

    @property
    def FB_STOPPED(self):
        """Message constant 'FB_STOPPED'."""
        return Metaclass_MissionControl.__constants['FB_STOPPED']

    @property
    def FB_PAUSED(self):
        """Message constant 'FB_PAUSED'."""
        return Metaclass_MissionControl.__constants['FB_PAUSED']

    @property
    def FB_EMERGENCY(self):
        """Message constant 'FB_EMERGENCY'."""
        return Metaclass_MissionControl.__constants['FB_EMERGENCY']

    @property
    def FB_RECEIVED(self):
        """Message constant 'FB_RECEIVED'."""
        return Metaclass_MissionControl.__constants['FB_RECEIVED']

    @property
    def FB_COMPLETED(self):
        """Message constant 'FB_COMPLETED'."""
        return Metaclass_MissionControl.__constants['FB_COMPLETED']


class MissionControl(metaclass=Metaclass_MissionControl):
    """
    Message class 'MissionControl'.

    Constants:
      CMD_START
      CMD_STOP
      CMD_PAUSE
      CMD_EMERGENCY
      CMD_SET_PLAN
      CMD_IS_FEEDBACK
      CMD_REQUEST_FEEDBACK
      FB_RUNNING
      FB_STOPPED
      FB_PAUSED
      FB_EMERGENCY
      FB_RECEIVED
      FB_COMPLETED
    """

    __slots__ = [
        '_name',
        '_hash',
        '_timeout',
        '_command',
        '_plan_state',
        '_feedback_str',
        '_waypoints',
    ]

    _fields_and_field_types = {
        'name': 'string',
        'hash': 'string',
        'timeout': 'uint64',
        'command': 'uint8',
        'plan_state': 'uint8',
        'feedback_str': 'string',
        'waypoints': 'sequence<smarc_mission_msgs/GotoWaypoint>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['smarc_mission_msgs', 'msg'], 'GotoWaypoint')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.name = kwargs.get('name', str())
        self.hash = kwargs.get('hash', str())
        self.timeout = kwargs.get('timeout', int())
        self.command = kwargs.get('command', int())
        self.plan_state = kwargs.get('plan_state', int())
        self.feedback_str = kwargs.get('feedback_str', str())
        self.waypoints = kwargs.get('waypoints', [])

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
        if self.name != other.name:
            return False
        if self.hash != other.hash:
            return False
        if self.timeout != other.timeout:
            return False
        if self.command != other.command:
            return False
        if self.plan_state != other.plan_state:
            return False
        if self.feedback_str != other.feedback_str:
            return False
        if self.waypoints != other.waypoints:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

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

    @builtins.property  # noqa: A003
    def hash(self):  # noqa: A003
        """Message field 'hash'."""
        return self._hash

    @hash.setter  # noqa: A003
    def hash(self, value):  # noqa: A003
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'hash' field must be of type 'str'"
        self._hash = value

    @builtins.property
    def timeout(self):
        """Message field 'timeout'."""
        return self._timeout

    @timeout.setter
    def timeout(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'timeout' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'timeout' field must be an unsigned integer in [0, 18446744073709551615]"
        self._timeout = value

    @builtins.property
    def command(self):
        """Message field 'command'."""
        return self._command

    @command.setter
    def command(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'command' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'command' field must be an unsigned integer in [0, 255]"
        self._command = value

    @builtins.property
    def plan_state(self):
        """Message field 'plan_state'."""
        return self._plan_state

    @plan_state.setter
    def plan_state(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'plan_state' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'plan_state' field must be an unsigned integer in [0, 255]"
        self._plan_state = value

    @builtins.property
    def feedback_str(self):
        """Message field 'feedback_str'."""
        return self._feedback_str

    @feedback_str.setter
    def feedback_str(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'feedback_str' field must be of type 'str'"
        self._feedback_str = value

    @builtins.property
    def waypoints(self):
        """Message field 'waypoints'."""
        return self._waypoints

    @waypoints.setter
    def waypoints(self, value):
        if __debug__:
            from smarc_mission_msgs.msg import GotoWaypoint
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
                 all(isinstance(v, GotoWaypoint) for v in value) and
                 True), \
                "The 'waypoints' field must be a set or sequence and each value of type 'GotoWaypoint'"
        self._waypoints = value
