# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:msg/Topics.idl
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
        'DUBINS_SERVICE': 'mission/dubins_service',
        'UTM_LATLON_CONVERSION_SERVICE': 'mission/utm_latlon_conversion_service',
        'MISSION_COMPLETE_TOPIC': 'mission/complete',
        'MISSION_CONTROL_TOPIC': 'mission/mission_control',
        'BT_COMMAND_TOPIC': 'mission/bt_command',
        'BT_TIP_TOPIC': 'mission/bt_tip',
        'BT_LAST_WP_TOPIC': 'mission/last_wp',
        'GOTO_WP_ACTION': 'mission/goto_wp_action',
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
                'smarc_mission_msgs.msg.Topics')
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
            'DUBINS_SERVICE': cls.__constants['DUBINS_SERVICE'],
            'UTM_LATLON_CONVERSION_SERVICE': cls.__constants['UTM_LATLON_CONVERSION_SERVICE'],
            'MISSION_COMPLETE_TOPIC': cls.__constants['MISSION_COMPLETE_TOPIC'],
            'MISSION_CONTROL_TOPIC': cls.__constants['MISSION_CONTROL_TOPIC'],
            'BT_COMMAND_TOPIC': cls.__constants['BT_COMMAND_TOPIC'],
            'BT_TIP_TOPIC': cls.__constants['BT_TIP_TOPIC'],
            'BT_LAST_WP_TOPIC': cls.__constants['BT_LAST_WP_TOPIC'],
            'GOTO_WP_ACTION': cls.__constants['GOTO_WP_ACTION'],
        }

    @property
    def DUBINS_SERVICE(self):
        """Message constant 'DUBINS_SERVICE'."""
        return Metaclass_Topics.__constants['DUBINS_SERVICE']

    @property
    def UTM_LATLON_CONVERSION_SERVICE(self):
        """Message constant 'UTM_LATLON_CONVERSION_SERVICE'."""
        return Metaclass_Topics.__constants['UTM_LATLON_CONVERSION_SERVICE']

    @property
    def MISSION_COMPLETE_TOPIC(self):
        """Message constant 'MISSION_COMPLETE_TOPIC'."""
        return Metaclass_Topics.__constants['MISSION_COMPLETE_TOPIC']

    @property
    def MISSION_CONTROL_TOPIC(self):
        """Message constant 'MISSION_CONTROL_TOPIC'."""
        return Metaclass_Topics.__constants['MISSION_CONTROL_TOPIC']

    @property
    def BT_COMMAND_TOPIC(self):
        """Message constant 'BT_COMMAND_TOPIC'."""
        return Metaclass_Topics.__constants['BT_COMMAND_TOPIC']

    @property
    def BT_TIP_TOPIC(self):
        """Message constant 'BT_TIP_TOPIC'."""
        return Metaclass_Topics.__constants['BT_TIP_TOPIC']

    @property
    def BT_LAST_WP_TOPIC(self):
        """Message constant 'BT_LAST_WP_TOPIC'."""
        return Metaclass_Topics.__constants['BT_LAST_WP_TOPIC']

    @property
    def GOTO_WP_ACTION(self):
        """Message constant 'GOTO_WP_ACTION'."""
        return Metaclass_Topics.__constants['GOTO_WP_ACTION']


class Topics(metaclass=Metaclass_Topics):
    """
    Message class 'Topics'.

    Constants:
      DUBINS_SERVICE
      UTM_LATLON_CONVERSION_SERVICE
      MISSION_COMPLETE_TOPIC
      MISSION_CONTROL_TOPIC
      BT_COMMAND_TOPIC
      BT_TIP_TOPIC
      BT_LAST_WP_TOPIC
      GOTO_WP_ACTION
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
