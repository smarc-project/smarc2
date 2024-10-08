# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/ThrusterFeedback.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ThrusterFeedback(type):
    """Metaclass of message 'ThrusterFeedback'."""

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
                'smarc_msgs.msg.ThrusterFeedback')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__thruster_feedback
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__thruster_feedback
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__thruster_feedback
            cls._TYPE_SUPPORT = module.type_support_msg__msg__thruster_feedback
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__thruster_feedback

            from smarc_msgs.msg import ThrusterDC
            if ThrusterDC.__class__._TYPE_SUPPORT is None:
                ThrusterDC.__class__.__import_type_support__()

            from smarc_msgs.msg import ThrusterRPM
            if ThrusterRPM.__class__._TYPE_SUPPORT is None:
                ThrusterRPM.__class__.__import_type_support__()

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


class ThrusterFeedback(metaclass=Metaclass_ThrusterFeedback):
    """Message class 'ThrusterFeedback'."""

    __slots__ = [
        '_header',
        '_rpm',
        '_dc',
        '_current',
        '_torque',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'rpm': 'smarc_msgs/ThrusterRPM',
        'dc': 'smarc_msgs/ThrusterDC',
        'current': 'float',
        'torque': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['smarc_msgs', 'msg'], 'ThrusterRPM'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['smarc_msgs', 'msg'], 'ThrusterDC'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        from smarc_msgs.msg import ThrusterRPM
        self.rpm = kwargs.get('rpm', ThrusterRPM())
        from smarc_msgs.msg import ThrusterDC
        self.dc = kwargs.get('dc', ThrusterDC())
        self.current = kwargs.get('current', float())
        self.torque = kwargs.get('torque', float())

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
        if self.rpm != other.rpm:
            return False
        if self.dc != other.dc:
            return False
        if self.current != other.current:
            return False
        if self.torque != other.torque:
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

    @builtins.property
    def rpm(self):
        """Message field 'rpm'."""
        return self._rpm

    @rpm.setter
    def rpm(self, value):
        if __debug__:
            from smarc_msgs.msg import ThrusterRPM
            assert \
                isinstance(value, ThrusterRPM), \
                "The 'rpm' field must be a sub message of type 'ThrusterRPM'"
        self._rpm = value

    @builtins.property
    def dc(self):
        """Message field 'dc'."""
        return self._dc

    @dc.setter
    def dc(self, value):
        if __debug__:
            from smarc_msgs.msg import ThrusterDC
            assert \
                isinstance(value, ThrusterDC), \
                "The 'dc' field must be a sub message of type 'ThrusterDC'"
        self._dc = value

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

    @builtins.property
    def torque(self):
        """Message field 'torque'."""
        return self._torque

    @torque.setter
    def torque(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'torque' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'torque' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._torque = value
