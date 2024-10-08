# generated from rosidl_generator_py/resource/_idl.py.em
# with input from sam_msgs:msg/Command.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Command(type):
    """Metaclass of message 'Command'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'COMMAND_TYPE_UNITLESS': 0,
        'COMMAND_TYPE_POSITION': 1,
        'COMMAND_TYPE_FORCE': 2,
        'COMMAND_TYPE_SPEED': 3,
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
                'sam_msgs.msg.Command')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__command
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__command
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__command
            cls._TYPE_SUPPORT = module.type_support_msg__msg__command
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__command

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'COMMAND_TYPE_UNITLESS': cls.__constants['COMMAND_TYPE_UNITLESS'],
            'COMMAND_TYPE_POSITION': cls.__constants['COMMAND_TYPE_POSITION'],
            'COMMAND_TYPE_FORCE': cls.__constants['COMMAND_TYPE_FORCE'],
            'COMMAND_TYPE_SPEED': cls.__constants['COMMAND_TYPE_SPEED'],
        }

    @property
    def COMMAND_TYPE_UNITLESS(self):
        """Message constant 'COMMAND_TYPE_UNITLESS'."""
        return Metaclass_Command.__constants['COMMAND_TYPE_UNITLESS']

    @property
    def COMMAND_TYPE_POSITION(self):
        """Message constant 'COMMAND_TYPE_POSITION'."""
        return Metaclass_Command.__constants['COMMAND_TYPE_POSITION']

    @property
    def COMMAND_TYPE_FORCE(self):
        """Message constant 'COMMAND_TYPE_FORCE'."""
        return Metaclass_Command.__constants['COMMAND_TYPE_FORCE']

    @property
    def COMMAND_TYPE_SPEED(self):
        """Message constant 'COMMAND_TYPE_SPEED'."""
        return Metaclass_Command.__constants['COMMAND_TYPE_SPEED']


class Command(metaclass=Metaclass_Command):
    """
    Message class 'Command'.

    Constants:
      COMMAND_TYPE_UNITLESS
      COMMAND_TYPE_POSITION
      COMMAND_TYPE_FORCE
      COMMAND_TYPE_SPEED
    """

    __slots__ = [
        '_actuator_id',
        '_command_type',
        '_command_value',
    ]

    _fields_and_field_types = {
        'actuator_id': 'uint8',
        'command_type': 'uint8',
        'command_value': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.actuator_id = kwargs.get('actuator_id', int())
        self.command_type = kwargs.get('command_type', int())
        self.command_value = kwargs.get('command_value', float())

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
        if self.actuator_id != other.actuator_id:
            return False
        if self.command_type != other.command_type:
            return False
        if self.command_value != other.command_value:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def actuator_id(self):
        """Message field 'actuator_id'."""
        return self._actuator_id

    @actuator_id.setter
    def actuator_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'actuator_id' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'actuator_id' field must be an unsigned integer in [0, 255]"
        self._actuator_id = value

    @builtins.property
    def command_type(self):
        """Message field 'command_type'."""
        return self._command_type

    @command_type.setter
    def command_type(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'command_type' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'command_type' field must be an unsigned integer in [0, 255]"
        self._command_type = value

    @builtins.property
    def command_value(self):
        """Message field 'command_value'."""
        return self._command_value

    @command_value.setter
    def command_value(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'command_value' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'command_value' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._command_value = value
