# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/Topics.idl
# generated code does not contain a copyright notice


# Import statements for member types

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_Topics(type):
    """Metaclass of message 'Topics'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'BATTERY_TOPIC': 'core/battery',
        'GPS_TOPIC': 'core/gps',
        'HEADING_TOPIC': 'core/heading',
        'ABORT_TOPIC': 'core/abort',
        'HEARTBEAT_TOPIC': 'core/heartbeat',
        'VEHICLE_READY_TOPIC': 'core/vehicle_ready',
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
                'smarc_msgs.msg.Topics')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__topics
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__topics
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__topics
            cls._TYPE_SUPPORT = module.type_support_msg__msg__topics
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__topics

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'BATTERY_TOPIC': cls.__constants['BATTERY_TOPIC'],
            'GPS_TOPIC': cls.__constants['GPS_TOPIC'],
            'HEADING_TOPIC': cls.__constants['HEADING_TOPIC'],
            'ABORT_TOPIC': cls.__constants['ABORT_TOPIC'],
            'HEARTBEAT_TOPIC': cls.__constants['HEARTBEAT_TOPIC'],
            'VEHICLE_READY_TOPIC': cls.__constants['VEHICLE_READY_TOPIC'],
        }

    @property
    def BATTERY_TOPIC(self):
        """Message constant 'BATTERY_TOPIC'."""
        return Metaclass_Topics.__constants['BATTERY_TOPIC']

    @property
    def GPS_TOPIC(self):
        """Message constant 'GPS_TOPIC'."""
        return Metaclass_Topics.__constants['GPS_TOPIC']

    @property
    def HEADING_TOPIC(self):
        """Message constant 'HEADING_TOPIC'."""
        return Metaclass_Topics.__constants['HEADING_TOPIC']

    @property
    def ABORT_TOPIC(self):
        """Message constant 'ABORT_TOPIC'."""
        return Metaclass_Topics.__constants['ABORT_TOPIC']

    @property
    def HEARTBEAT_TOPIC(self):
        """Message constant 'HEARTBEAT_TOPIC'."""
        return Metaclass_Topics.__constants['HEARTBEAT_TOPIC']

    @property
    def VEHICLE_READY_TOPIC(self):
        """Message constant 'VEHICLE_READY_TOPIC'."""
        return Metaclass_Topics.__constants['VEHICLE_READY_TOPIC']


class Topics(metaclass=Metaclass_Topics):
    """
    Message class 'Topics'.

    Constants:
      BATTERY_TOPIC
      GPS_TOPIC
      HEADING_TOPIC
      ABORT_TOPIC
      HEARTBEAT_TOPIC
      VEHICLE_READY_TOPIC
    """

    __slots__ = [
    ]

    _fields_and_field_types = {
    }

    SLOT_TYPES = (
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))

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
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)
