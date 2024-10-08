# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/DualThrusterFeedback.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_DualThrusterFeedback(type):
    """Metaclass of message 'DualThrusterFeedback'."""

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
                'smarc_msgs.msg.DualThrusterFeedback')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__dual_thruster_feedback
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__dual_thruster_feedback
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__dual_thruster_feedback
            cls._TYPE_SUPPORT = module.type_support_msg__msg__dual_thruster_feedback
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__dual_thruster_feedback

            from smarc_msgs.msg import ThrusterFeedback
            if ThrusterFeedback.__class__._TYPE_SUPPORT is None:
                ThrusterFeedback.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DualThrusterFeedback(metaclass=Metaclass_DualThrusterFeedback):
    """Message class 'DualThrusterFeedback'."""

    __slots__ = [
        '_thruster_front',
        '_thruster_back',
    ]

    _fields_and_field_types = {
        'thruster_front': 'smarc_msgs/ThrusterFeedback',
        'thruster_back': 'smarc_msgs/ThrusterFeedback',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['smarc_msgs', 'msg'], 'ThrusterFeedback'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['smarc_msgs', 'msg'], 'ThrusterFeedback'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from smarc_msgs.msg import ThrusterFeedback
        self.thruster_front = kwargs.get('thruster_front', ThrusterFeedback())
        from smarc_msgs.msg import ThrusterFeedback
        self.thruster_back = kwargs.get('thruster_back', ThrusterFeedback())

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
        if self.thruster_front != other.thruster_front:
            return False
        if self.thruster_back != other.thruster_back:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def thruster_front(self):
        """Message field 'thruster_front'."""
        return self._thruster_front

    @thruster_front.setter
    def thruster_front(self, value):
        if __debug__:
            from smarc_msgs.msg import ThrusterFeedback
            assert \
                isinstance(value, ThrusterFeedback), \
                "The 'thruster_front' field must be a sub message of type 'ThrusterFeedback'"
        self._thruster_front = value

    @builtins.property
    def thruster_back(self):
        """Message field 'thruster_back'."""
        return self._thruster_back

    @thruster_back.setter
    def thruster_back(self, value):
        if __debug__:
            from smarc_msgs.msg import ThrusterFeedback
            assert \
                isinstance(value, ThrusterFeedback), \
                "The 'thruster_back' field must be a sub message of type 'ThrusterFeedback'"
        self._thruster_back = value
