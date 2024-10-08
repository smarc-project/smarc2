# generated from rosidl_generator_py/resource/_idl.py.em
# with input from sam_msgs:msg/CircuitStatus.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_CircuitStatus(type):
    """Metaclass of message 'CircuitStatus'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'ERROR_FLAG_OVERVOLTAGE': 1,
        'ERROR_FLAG_UNDERVOLTAGE': 2,
        'ERROR_FLAG_OVERCURRENT': 4,
        'ERROR_FLAG_UNDERCURRENT': 8,
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('sam_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'sam_msgs.msg.CircuitStatus')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__circuit_status
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__circuit_status
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__circuit_status
            cls._TYPE_SUPPORT = module.type_support_msg__msg__circuit_status
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__circuit_status

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'ERROR_FLAG_OVERVOLTAGE': cls.__constants['ERROR_FLAG_OVERVOLTAGE'],
            'ERROR_FLAG_UNDERVOLTAGE': cls.__constants['ERROR_FLAG_UNDERVOLTAGE'],
            'ERROR_FLAG_OVERCURRENT': cls.__constants['ERROR_FLAG_OVERCURRENT'],
            'ERROR_FLAG_UNDERCURRENT': cls.__constants['ERROR_FLAG_UNDERCURRENT'],
        }

    @property
    def ERROR_FLAG_OVERVOLTAGE(self):
        """Message constant 'ERROR_FLAG_OVERVOLTAGE'."""
        return Metaclass_CircuitStatus.__constants['ERROR_FLAG_OVERVOLTAGE']

    @property
    def ERROR_FLAG_UNDERVOLTAGE(self):
        """Message constant 'ERROR_FLAG_UNDERVOLTAGE'."""
        return Metaclass_CircuitStatus.__constants['ERROR_FLAG_UNDERVOLTAGE']

    @property
    def ERROR_FLAG_OVERCURRENT(self):
        """Message constant 'ERROR_FLAG_OVERCURRENT'."""
        return Metaclass_CircuitStatus.__constants['ERROR_FLAG_OVERCURRENT']

    @property
    def ERROR_FLAG_UNDERCURRENT(self):
        """Message constant 'ERROR_FLAG_UNDERCURRENT'."""
        return Metaclass_CircuitStatus.__constants['ERROR_FLAG_UNDERCURRENT']


class CircuitStatus(metaclass=Metaclass_CircuitStatus):
    """
    Message class 'CircuitStatus'.

    Constants:
      ERROR_FLAG_OVERVOLTAGE
      ERROR_FLAG_UNDERVOLTAGE
      ERROR_FLAG_OVERCURRENT
      ERROR_FLAG_UNDERCURRENT
    """

    __slots__ = [
        '_error_flags',
        '_circuit_id',
        '_voltage',
        '_current',
    ]

    _fields_and_field_types = {
        'error_flags': 'uint8',
        'circuit_id': 'uint16',
        'voltage': 'float',
        'current': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint16'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.error_flags = kwargs.get('error_flags', int())
        self.circuit_id = kwargs.get('circuit_id', int())
        self.voltage = kwargs.get('voltage', float())
        self.current = kwargs.get('current', float())

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
        if self.error_flags != other.error_flags:
            return False
        if self.circuit_id != other.circuit_id:
            return False
        if self.voltage != other.voltage:
            return False
        if self.current != other.current:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def error_flags(self):
        """Message field 'error_flags'."""
        return self._error_flags

    @error_flags.setter
    def error_flags(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'error_flags' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'error_flags' field must be an unsigned integer in [0, 255]"
        self._error_flags = value

    @builtins.property
    def circuit_id(self):
        """Message field 'circuit_id'."""
        return self._circuit_id

    @circuit_id.setter
    def circuit_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'circuit_id' field must be of type 'int'"
            assert value >= 0 and value < 65536, \
                "The 'circuit_id' field must be an unsigned integer in [0, 65535]"
        self._circuit_id = value

    @builtins.property
    def voltage(self):
        """Message field 'voltage'."""
        return self._voltage

    @voltage.setter
    def voltage(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'voltage' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'voltage' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._voltage = value

    @builtins.property
    def current(self):
        """Message field 'current'."""
        return self._current

    @current.setter
    def current(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'current' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'current' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._current = value
