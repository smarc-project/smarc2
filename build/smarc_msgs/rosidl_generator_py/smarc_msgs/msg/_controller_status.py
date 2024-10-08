# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/ControllerStatus.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_ControllerStatus(type):
    """Metaclass of message 'ControllerStatus'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'CONTROL_STATUS_NOT_CONTROLLING': 0,
        'CONTROL_STATUS_CONTROLLING': 1,
        'CONTROL_STATUS_ERROR': 2,
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
                'smarc_msgs.msg.ControllerStatus')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__controller_status
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__controller_status
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__controller_status
            cls._TYPE_SUPPORT = module.type_support_msg__msg__controller_status
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__controller_status

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'CONTROL_STATUS_NOT_CONTROLLING': cls.__constants['CONTROL_STATUS_NOT_CONTROLLING'],
            'CONTROL_STATUS_CONTROLLING': cls.__constants['CONTROL_STATUS_CONTROLLING'],
            'CONTROL_STATUS_ERROR': cls.__constants['CONTROL_STATUS_ERROR'],
        }

    @property
    def CONTROL_STATUS_NOT_CONTROLLING(self):
        """Message constant 'CONTROL_STATUS_NOT_CONTROLLING'."""
        return Metaclass_ControllerStatus.__constants['CONTROL_STATUS_NOT_CONTROLLING']

    @property
    def CONTROL_STATUS_CONTROLLING(self):
        """Message constant 'CONTROL_STATUS_CONTROLLING'."""
        return Metaclass_ControllerStatus.__constants['CONTROL_STATUS_CONTROLLING']

    @property
    def CONTROL_STATUS_ERROR(self):
        """Message constant 'CONTROL_STATUS_ERROR'."""
        return Metaclass_ControllerStatus.__constants['CONTROL_STATUS_ERROR']


class ControllerStatus(metaclass=Metaclass_ControllerStatus):
    """
    Message class 'ControllerStatus'.

    Constants:
      CONTROL_STATUS_NOT_CONTROLLING
      CONTROL_STATUS_CONTROLLING
      CONTROL_STATUS_ERROR
    """

    __slots__ = [
        '_control_status',
        '_service_name',
        '_diagnostics_message',
    ]

    _fields_and_field_types = {
        'control_status': 'uint8',
        'service_name': 'string',
        'diagnostics_message': 'string',
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
        self.control_status = kwargs.get('control_status', int())
        self.service_name = kwargs.get('service_name', str())
        self.diagnostics_message = kwargs.get('diagnostics_message', str())

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
        if self.control_status != other.control_status:
            return False
        if self.service_name != other.service_name:
            return False
        if self.diagnostics_message != other.diagnostics_message:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def control_status(self):
        """Message field 'control_status'."""
        return self._control_status

    @control_status.setter
    def control_status(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'control_status' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'control_status' field must be an unsigned integer in [0, 255]"
        self._control_status = value

    @builtins.property
    def service_name(self):
        """Message field 'service_name'."""
        return self._service_name

    @service_name.setter
    def service_name(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'service_name' field must be of type 'str'"
        self._service_name = value

    @builtins.property
    def diagnostics_message(self):
        """Message field 'diagnostics_message'."""
        return self._diagnostics_message

    @diagnostics_message.setter
    def diagnostics_message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'diagnostics_message' field must be of type 'str'"
        self._diagnostics_message = value
