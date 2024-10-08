# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_control_msgs:msg/ControlInput.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ControlInput(type):
    """Metaclass of message 'ControlInput'."""

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
            module = import_type_support('smarc_control_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_control_msgs.msg.ControlInput')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__control_input
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__control_input
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__control_input
            cls._TYPE_SUPPORT = module.type_support_msg__msg__control_input
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__control_input

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class ControlInput(metaclass=Metaclass_ControlInput):
    """Message class 'ControlInput'."""

    __slots__ = [
        '_thrusterrpm',
        '_thrustervertical',
        '_thrusterhorizontal',
        '_vbs',
        '_lcg',
    ]

    _fields_and_field_types = {
        'thrusterrpm': 'double',
        'thrustervertical': 'double',
        'thrusterhorizontal': 'double',
        'vbs': 'double',
        'lcg': 'double',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
        rosidl_parser.definition.BasicType('double'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.thrusterrpm = kwargs.get('thrusterrpm', float())
        self.thrustervertical = kwargs.get('thrustervertical', float())
        self.thrusterhorizontal = kwargs.get('thrusterhorizontal', float())
        self.vbs = kwargs.get('vbs', float())
        self.lcg = kwargs.get('lcg', float())

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
        if self.thrusterrpm != other.thrusterrpm:
            return False
        if self.thrustervertical != other.thrustervertical:
            return False
        if self.thrusterhorizontal != other.thrusterhorizontal:
            return False
        if self.vbs != other.vbs:
            return False
        if self.lcg != other.lcg:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def thrusterrpm(self):
        """Message field 'thrusterrpm'."""
        return self._thrusterrpm

    @thrusterrpm.setter
    def thrusterrpm(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'thrusterrpm' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'thrusterrpm' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._thrusterrpm = value

    @builtins.property
    def thrustervertical(self):
        """Message field 'thrustervertical'."""
        return self._thrustervertical

    @thrustervertical.setter
    def thrustervertical(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'thrustervertical' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'thrustervertical' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._thrustervertical = value

    @builtins.property
    def thrusterhorizontal(self):
        """Message field 'thrusterhorizontal'."""
        return self._thrusterhorizontal

    @thrusterhorizontal.setter
    def thrusterhorizontal(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'thrusterhorizontal' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'thrusterhorizontal' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._thrusterhorizontal = value

    @builtins.property
    def vbs(self):
        """Message field 'vbs'."""
        return self._vbs

    @vbs.setter
    def vbs(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'vbs' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'vbs' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._vbs = value

    @builtins.property
    def lcg(self):
        """Message field 'lcg'."""
        return self._lcg

    @lcg.setter
    def lcg(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'lcg' field must be of type 'float'"
            assert not (value < -1.7976931348623157e+308 or value > 1.7976931348623157e+308) or math.isinf(value), \
                "The 'lcg' field must be a double in [-1.7976931348623157e+308, 1.7976931348623157e+308]"
        self._lcg = value
