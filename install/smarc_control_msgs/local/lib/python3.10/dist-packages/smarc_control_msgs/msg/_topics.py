# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_control_msgs:msg/Topics.idl
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
        'STATES': 'core/odom_gt',
        'DEPTH_SETPOINT': 'ctrl/depth_setpoint',
        'PITCH_SETPOINT': 'ctrl/pitch_setpoint',
        'STATES_CONV': 'ctrl/conv/states',
        'REF_CONV': 'ctrl/conv/ref',
        'CONTROL_ERROR_CONV': 'ctrl/conv/error',
        'CONTROL_INPUT_CONV': 'ctrl/conv/control_input',
        'WAYPOINT_CONV': 'ctrl/conv/waypoint',
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
                'smarc_control_msgs.msg.Topics')
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
            'STATES': cls.__constants['STATES'],
            'DEPTH_SETPOINT': cls.__constants['DEPTH_SETPOINT'],
            'PITCH_SETPOINT': cls.__constants['PITCH_SETPOINT'],
            'STATES_CONV': cls.__constants['STATES_CONV'],
            'REF_CONV': cls.__constants['REF_CONV'],
            'CONTROL_ERROR_CONV': cls.__constants['CONTROL_ERROR_CONV'],
            'CONTROL_INPUT_CONV': cls.__constants['CONTROL_INPUT_CONV'],
            'WAYPOINT_CONV': cls.__constants['WAYPOINT_CONV'],
        }

    @property
    def STATES(self):
        """Message constant 'STATES'."""
        return Metaclass_Topics.__constants['STATES']

    @property
    def DEPTH_SETPOINT(self):
        """Message constant 'DEPTH_SETPOINT'."""
        return Metaclass_Topics.__constants['DEPTH_SETPOINT']

    @property
    def PITCH_SETPOINT(self):
        """Message constant 'PITCH_SETPOINT'."""
        return Metaclass_Topics.__constants['PITCH_SETPOINT']

    @property
    def STATES_CONV(self):
        """Message constant 'STATES_CONV'."""
        return Metaclass_Topics.__constants['STATES_CONV']

    @property
    def REF_CONV(self):
        """Message constant 'REF_CONV'."""
        return Metaclass_Topics.__constants['REF_CONV']

    @property
    def CONTROL_ERROR_CONV(self):
        """Message constant 'CONTROL_ERROR_CONV'."""
        return Metaclass_Topics.__constants['CONTROL_ERROR_CONV']

    @property
    def CONTROL_INPUT_CONV(self):
        """Message constant 'CONTROL_INPUT_CONV'."""
        return Metaclass_Topics.__constants['CONTROL_INPUT_CONV']

    @property
    def WAYPOINT_CONV(self):
        """Message constant 'WAYPOINT_CONV'."""
        return Metaclass_Topics.__constants['WAYPOINT_CONV']


class Topics(metaclass=Metaclass_Topics):
    """
    Message class 'Topics'.

    Constants:
      STATES
      DEPTH_SETPOINT
      PITCH_SETPOINT
      STATES_CONV
      REF_CONV
      CONTROL_ERROR_CONV
      CONTROL_INPUT_CONV
      WAYPOINT_CONV
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
