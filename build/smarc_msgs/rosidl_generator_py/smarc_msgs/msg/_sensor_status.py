# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:msg/SensorStatus.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_SensorStatus(type):
    """Metaclass of message 'SensorStatus'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'SENSOR_STATUS_NOT_ACTIVE': 0,
        'SENSOR_STATUS_ACTIVE': 1,
        'SENSOR_STATUS_ERROR': 2,
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
                'smarc_msgs.msg.SensorStatus')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__sensor_status
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__sensor_status
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__sensor_status
            cls._TYPE_SUPPORT = module.type_support_msg__msg__sensor_status
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__sensor_status

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'SENSOR_STATUS_NOT_ACTIVE': cls.__constants['SENSOR_STATUS_NOT_ACTIVE'],
            'SENSOR_STATUS_ACTIVE': cls.__constants['SENSOR_STATUS_ACTIVE'],
            'SENSOR_STATUS_ERROR': cls.__constants['SENSOR_STATUS_ERROR'],
        }

    @property
    def SENSOR_STATUS_NOT_ACTIVE(self):
        """Message constant 'SENSOR_STATUS_NOT_ACTIVE'."""
        return Metaclass_SensorStatus.__constants['SENSOR_STATUS_NOT_ACTIVE']

    @property
    def SENSOR_STATUS_ACTIVE(self):
        """Message constant 'SENSOR_STATUS_ACTIVE'."""
        return Metaclass_SensorStatus.__constants['SENSOR_STATUS_ACTIVE']

    @property
    def SENSOR_STATUS_ERROR(self):
        """Message constant 'SENSOR_STATUS_ERROR'."""
        return Metaclass_SensorStatus.__constants['SENSOR_STATUS_ERROR']


class SensorStatus(metaclass=Metaclass_SensorStatus):
    """
    Message class 'SensorStatus'.

    Constants:
      SENSOR_STATUS_NOT_ACTIVE
      SENSOR_STATUS_ACTIVE
      SENSOR_STATUS_ERROR
    """

    __slots__ = [
        '_sensor_status',
        '_service_name',
        '_diagnostics_message',
    ]

    _fields_and_field_types = {
        'sensor_status': 'uint8',
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
        self.sensor_status = kwargs.get('sensor_status', int())
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
        if self.sensor_status != other.sensor_status:
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
    def sensor_status(self):
        """Message field 'sensor_status'."""
        return self._sensor_status

    @sensor_status.setter
    def sensor_status(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'sensor_status' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'sensor_status' field must be an unsigned integer in [0, 255]"
        self._sensor_status = value

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
