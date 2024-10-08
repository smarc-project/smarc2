# generated from rosidl_generator_py/resource/_idl.py.em
# with input from sam_msgs:msg/ConsumedChargeFeedback.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ConsumedChargeFeedback(type):
    """Metaclass of message 'ConsumedChargeFeedback'."""

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
            module = import_type_support('sam_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'sam_msgs.msg.ConsumedChargeFeedback')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__consumed_charge_feedback
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__consumed_charge_feedback
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__consumed_charge_feedback
            cls._TYPE_SUPPORT = module.type_support_msg__msg__consumed_charge_feedback
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__consumed_charge_feedback

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


class ConsumedChargeFeedback(metaclass=Metaclass_ConsumedChargeFeedback):
    """Message class 'ConsumedChargeFeedback'."""

    __slots__ = [
        '_header',
        '_main',
        '_esc1',
        '_esc2',
        '_esc3',
        '_v20',
        '_v12',
        '_v7',
        '_v5',
        '_v33',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'main': 'float',
        'esc1': 'float',
        'esc2': 'float',
        'esc3': 'float',
        'v20': 'float',
        'v12': 'float',
        'v7': 'float',
        'v5': 'float',
        'v33': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.main = kwargs.get('main', float())
        self.esc1 = kwargs.get('esc1', float())
        self.esc2 = kwargs.get('esc2', float())
        self.esc3 = kwargs.get('esc3', float())
        self.v20 = kwargs.get('v20', float())
        self.v12 = kwargs.get('v12', float())
        self.v7 = kwargs.get('v7', float())
        self.v5 = kwargs.get('v5', float())
        self.v33 = kwargs.get('v33', float())

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
        if self.main != other.main:
            return False
        if self.esc1 != other.esc1:
            return False
        if self.esc2 != other.esc2:
            return False
        if self.esc3 != other.esc3:
            return False
        if self.v20 != other.v20:
            return False
        if self.v12 != other.v12:
            return False
        if self.v7 != other.v7:
            return False
        if self.v5 != other.v5:
            return False
        if self.v33 != other.v33:
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
    def main(self):
        """Message field 'main'."""
        return self._main

    @main.setter
    def main(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'main' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'main' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._main = value

    @builtins.property
    def esc1(self):
        """Message field 'esc1'."""
        return self._esc1

    @esc1.setter
    def esc1(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'esc1' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'esc1' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._esc1 = value

    @builtins.property
    def esc2(self):
        """Message field 'esc2'."""
        return self._esc2

    @esc2.setter
    def esc2(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'esc2' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'esc2' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._esc2 = value

    @builtins.property
    def esc3(self):
        """Message field 'esc3'."""
        return self._esc3

    @esc3.setter
    def esc3(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'esc3' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'esc3' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._esc3 = value

    @builtins.property
    def v20(self):
        """Message field 'v20'."""
        return self._v20

    @v20.setter
    def v20(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'v20' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v20' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v20 = value

    @builtins.property
    def v12(self):
        """Message field 'v12'."""
        return self._v12

    @v12.setter
    def v12(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'v12' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v12' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v12 = value

    @builtins.property
    def v7(self):
        """Message field 'v7'."""
        return self._v7

    @v7.setter
    def v7(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'v7' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v7' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v7 = value

    @builtins.property
    def v5(self):
        """Message field 'v5'."""
        return self._v5

    @v5.setter
    def v5(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'v5' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v5' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v5 = value

    @builtins.property
    def v33(self):
        """Message field 'v33'."""
        return self._v33

    @v33.setter
    def v33(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'v33' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'v33' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._v33 = value
