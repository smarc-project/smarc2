# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:msg/BTCommand.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_BTCommand(type):
    """Metaclass of message 'BTCommand'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'TYPE_CMD': 0,
        'TYPE_FB': 1,
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
                'smarc_mission_msgs.msg.BTCommand')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__bt_command
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__bt_command
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__bt_command
            cls._TYPE_SUPPORT = module.type_support_msg__msg__bt_command
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__bt_command

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'TYPE_CMD': cls.__constants['TYPE_CMD'],
            'TYPE_FB': cls.__constants['TYPE_FB'],
        }

    @property
    def TYPE_CMD(self):
        """Message constant 'TYPE_CMD'."""
        return Metaclass_BTCommand.__constants['TYPE_CMD']

    @property
    def TYPE_FB(self):
        """Message constant 'TYPE_FB'."""
        return Metaclass_BTCommand.__constants['TYPE_FB']


class BTCommand(metaclass=Metaclass_BTCommand):
    """
    Message class 'BTCommand'.

    Constants:
      TYPE_CMD
      TYPE_FB
    """

    __slots__ = [
        '_msg_type',
        '_cmd_json',
        '_fb_json',
    ]

    _fields_and_field_types = {
        'msg_type': 'uint8',
        'cmd_json': 'string',
        'fb_json': 'string',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.msg_type = kwargs.get('msg_type', int())
        self.cmd_json = kwargs.get('cmd_json', str())
        self.fb_json = kwargs.get('fb_json', str())

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
        if self.msg_type != other.msg_type:
            return False
        if self.cmd_json != other.cmd_json:
            return False
        if self.fb_json != other.fb_json:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def msg_type(self):
        """Message field 'msg_type'."""
        return self._msg_type

    @msg_type.setter
    def msg_type(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'msg_type' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'msg_type' field must be an unsigned integer in [0, 255]"
        self._msg_type = value

    @builtins.property
    def cmd_json(self):
        """Message field 'cmd_json'."""
        return self._cmd_json

    @cmd_json.setter
    def cmd_json(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'cmd_json' field must be of type 'str'"
        self._cmd_json = value

    @builtins.property
    def fb_json(self):
        """Message field 'fb_json'."""
        return self._fb_json

    @fb_json.setter
    def fb_json(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'fb_json' field must be of type 'str'"
        self._fb_json = value
