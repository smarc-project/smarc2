# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/Sidescan.idl
# generated code does not contain a copyright notice


# Import statements for member types

# Member 'port_channel'
# Member 'starboard_channel'
# Member 'port_channel_angle_high'
# Member 'port_channel_angle_low'
# Member 'starboard_channel_angle_high'
# Member 'starboard_channel_angle_low'
# Member 'extra_channel'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Sidescan(type):
    """Metaclass of message 'Sidescan'."""

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
                'smarc_msgs.msg.Sidescan')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__sidescan
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__sidescan
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__sidescan
            cls._TYPE_SUPPORT = module.type_support_msg__msg__sidescan
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__sidescan

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class Sidescan(metaclass=Metaclass_Sidescan):
    """Message class 'Sidescan'."""

    __slots__ = [
        '_header',
        '_type',
        '_time',
        '_frequency_id',
        '_gain',
        '_decimation',
        '_max_duration',
        '_port_channel',
        '_starboard_channel',
        '_port_channel_angle_high',
        '_port_channel_angle_low',
        '_starboard_channel_angle_high',
        '_starboard_channel_angle_low',
        '_extra_channel',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'type': 'uint8',
        'time': 'uint32',
        'frequency_id': 'uint8',
        'gain': 'int16',
        'decimation': 'uint16',
        'max_duration': 'float',
        'port_channel': 'sequence<uint8>',
        'starboard_channel': 'sequence<uint8>',
        'port_channel_angle_high': 'sequence<uint8>',
        'port_channel_angle_low': 'sequence<uint8>',
        'starboard_channel_angle_high': 'sequence<uint8>',
        'starboard_channel_angle_low': 'sequence<uint8>',
        'extra_channel': 'sequence<uint8>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('int16'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('uint8')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.type = kwargs.get('type', int())
        self.time = kwargs.get('time', int())
        self.frequency_id = kwargs.get('frequency_id', int())
        self.gain = kwargs.get('gain', int())
        self.decimation = kwargs.get('decimation', int())
        self.max_duration = kwargs.get('max_duration', float())
        self.port_channel = array.array('B', kwargs.get('port_channel', []))
        self.starboard_channel = array.array('B', kwargs.get('starboard_channel', []))
        self.port_channel_angle_high = array.array('B', kwargs.get('port_channel_angle_high', []))
        self.port_channel_angle_low = array.array('B', kwargs.get('port_channel_angle_low', []))
        self.starboard_channel_angle_high = array.array('B', kwargs.get('starboard_channel_angle_high', []))
        self.starboard_channel_angle_low = array.array('B', kwargs.get('starboard_channel_angle_low', []))
        self.extra_channel = array.array('B', kwargs.get('extra_channel', []))

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
        if self.header != other.header:
            return False
        if self.type != other.type:
            return False
        if self.time != other.time:
            return False
        if self.frequency_id != other.frequency_id:
            return False
        if self.gain != other.gain:
            return False
        if self.decimation != other.decimation:
            return False
        if self.max_duration != other.max_duration:
            return False
        if self.port_channel != other.port_channel:
            return False
        if self.starboard_channel != other.starboard_channel:
            return False
        if self.port_channel_angle_high != other.port_channel_angle_high:
            return False
        if self.port_channel_angle_low != other.port_channel_angle_low:
            return False
        if self.starboard_channel_angle_high != other.starboard_channel_angle_high:
            return False
        if self.starboard_channel_angle_low != other.starboard_channel_angle_low:
            return False
        if self.extra_channel != other.extra_channel:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if __debug__:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property  # noqa: A003
    def type(self):  # noqa: A003
        """Message field 'type'."""
        return self._type

    @type.setter  # noqa: A003
    def type(self, value):  # noqa: A003
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'type' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'type' field must be an unsigned integer in [0, 255]"
        self._type = value

    @builtins.property
    def time(self):
        """Message field 'time'."""
        return self._time

    @time.setter
    def time(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'time' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'time' field must be an unsigned integer in [0, 4294967295]"
        self._time = value

    @builtins.property
    def frequency_id(self):
        """Message field 'frequency_id'."""
        return self._frequency_id

    @frequency_id.setter
    def frequency_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'frequency_id' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'frequency_id' field must be an unsigned integer in [0, 255]"
        self._frequency_id = value

    @builtins.property
    def gain(self):
        """Message field 'gain'."""
        return self._gain

    @gain.setter
    def gain(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'gain' field must be of type 'int'"
            assert value >= -32768 and value < 32768, \
                "The 'gain' field must be an integer in [-32768, 32767]"
        self._gain = value

    @builtins.property
    def decimation(self):
        """Message field 'decimation'."""
        return self._decimation

    @decimation.setter
    def decimation(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'decimation' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'decimation' field must be an unsigned integer in [0, 65535]"
        self._decimation = value

    @builtins.property
    def max_duration(self):
        """Message field 'max_duration'."""
        return self._max_duration

    @max_duration.setter
    def max_duration(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'max_duration' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'max_duration' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._max_duration = value

    @builtins.property
    def port_channel(self):
        """Message field 'port_channel'."""
        return self._port_channel

    @port_channel.setter
    def port_channel(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'port_channel' array.array() must have the type code of 'B'"
            self._port_channel = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'port_channel' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._port_channel = array.array('B', value)

    @builtins.property
    def starboard_channel(self):
        """Message field 'starboard_channel'."""
        return self._starboard_channel

    @starboard_channel.setter
    def starboard_channel(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'starboard_channel' array.array() must have the type code of 'B'"
            self._starboard_channel = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'starboard_channel' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._starboard_channel = array.array('B', value)

    @builtins.property
    def port_channel_angle_high(self):
        """Message field 'port_channel_angle_high'."""
        return self._port_channel_angle_high

    @port_channel_angle_high.setter
    def port_channel_angle_high(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'port_channel_angle_high' array.array() must have the type code of 'B'"
            self._port_channel_angle_high = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'port_channel_angle_high' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._port_channel_angle_high = array.array('B', value)

    @builtins.property
    def port_channel_angle_low(self):
        """Message field 'port_channel_angle_low'."""
        return self._port_channel_angle_low

    @port_channel_angle_low.setter
    def port_channel_angle_low(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'port_channel_angle_low' array.array() must have the type code of 'B'"
            self._port_channel_angle_low = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'port_channel_angle_low' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._port_channel_angle_low = array.array('B', value)

    @builtins.property
    def starboard_channel_angle_high(self):
        """Message field 'starboard_channel_angle_high'."""
        return self._starboard_channel_angle_high

    @starboard_channel_angle_high.setter
    def starboard_channel_angle_high(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'starboard_channel_angle_high' array.array() must have the type code of 'B'"
            self._starboard_channel_angle_high = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'starboard_channel_angle_high' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._starboard_channel_angle_high = array.array('B', value)

    @builtins.property
    def starboard_channel_angle_low(self):
        """Message field 'starboard_channel_angle_low'."""
        return self._starboard_channel_angle_low

    @starboard_channel_angle_low.setter
    def starboard_channel_angle_low(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'starboard_channel_angle_low' array.array() must have the type code of 'B'"
            self._starboard_channel_angle_low = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'starboard_channel_angle_low' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._starboard_channel_angle_low = array.array('B', value)

    @builtins.property
    def extra_channel(self):
        """Message field 'extra_channel'."""
        return self._extra_channel

    @extra_channel.setter
    def extra_channel(self, value):
        if isinstance(value, array.array):
            assert value.typecode == 'B', \
                "The 'extra_channel' array.array() must have the type code of 'B'"
            self._extra_channel = value
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
                 all(val >= 0 and val < 256 for val in value)), \
                "The 'extra_channel' field must be a set or sequence and each value of type 'int' and each unsigned integer in [0, 255]"
        self._extra_channel = array.array('B', value)
