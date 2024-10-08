# generated from rosidl_generator_py/resource/_idl.py.em
# with input from sam_msgs:srv/UavcanUpdateBattery.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_UavcanUpdateBattery_Request(type):
    """Metaclass of message 'UavcanUpdateBattery_Request'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'IS_FULL': 1,
        'WAS_FULL': 2,
        'ADD_CHARGE': 3,
        'ON_MAINS': 4,
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
                'sam_msgs.srv.UavcanUpdateBattery_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__uavcan_update_battery__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__uavcan_update_battery__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__uavcan_update_battery__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__uavcan_update_battery__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__uavcan_update_battery__request

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'IS_FULL': cls.__constants['IS_FULL'],
            'WAS_FULL': cls.__constants['WAS_FULL'],
            'ADD_CHARGE': cls.__constants['ADD_CHARGE'],
            'ON_MAINS': cls.__constants['ON_MAINS'],
        }

    @property
    def IS_FULL(self):
        """Message constant 'IS_FULL'."""
        return Metaclass_UavcanUpdateBattery_Request.__constants['IS_FULL']

    @property
    def WAS_FULL(self):
        """Message constant 'WAS_FULL'."""
        return Metaclass_UavcanUpdateBattery_Request.__constants['WAS_FULL']

    @property
    def ADD_CHARGE(self):
        """Message constant 'ADD_CHARGE'."""
        return Metaclass_UavcanUpdateBattery_Request.__constants['ADD_CHARGE']

    @property
    def ON_MAINS(self):
        """Message constant 'ON_MAINS'."""
        return Metaclass_UavcanUpdateBattery_Request.__constants['ON_MAINS']


class UavcanUpdateBattery_Request(metaclass=Metaclass_UavcanUpdateBattery_Request):
    """
    Message class 'UavcanUpdateBattery_Request'.

    Constants:
      IS_FULL
      WAS_FULL
      ADD_CHARGE
      ON_MAINS
    """

    __slots__ = [
        '_node_id',
        '_command',
        '_charge',
    ]

    _fields_and_field_types = {
        'node_id': 'uint8',
        'command': 'uint8',
        'charge': 'float',
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
        self.node_id = kwargs.get('node_id', int())
        self.command = kwargs.get('command', int())
        self.charge = kwargs.get('charge', float())

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
        if self.node_id != other.node_id:
            return False
        if self.command != other.command:
            return False
        if self.charge != other.charge:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def node_id(self):
        """Message field 'node_id'."""
        return self._node_id

    @node_id.setter
    def node_id(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'node_id' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'node_id' field must be an unsigned integer in [0, 255]"
        self._node_id = value

    @builtins.property
    def command(self):
        """Message field 'command'."""
        return self._command

    @command.setter
    def command(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'command' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'command' field must be an unsigned integer in [0, 255]"
        self._command = value

    @builtins.property
    def charge(self):
        """Message field 'charge'."""
        return self._charge

    @charge.setter
    def charge(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'charge' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'charge' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._charge = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_UavcanUpdateBattery_Response(type):
    """Metaclass of message 'UavcanUpdateBattery_Response'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
        'UPDATE_SUCCESSFULL': 1,
        'UPDATE_FAILED': 0,
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
                'sam_msgs.srv.UavcanUpdateBattery_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__uavcan_update_battery__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__uavcan_update_battery__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__uavcan_update_battery__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__uavcan_update_battery__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__uavcan_update_battery__response

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
            'UPDATE_SUCCESSFULL': cls.__constants['UPDATE_SUCCESSFULL'],
            'UPDATE_FAILED': cls.__constants['UPDATE_FAILED'],
        }

    @property
    def UPDATE_SUCCESSFULL(self):
        """Message constant 'UPDATE_SUCCESSFULL'."""
        return Metaclass_UavcanUpdateBattery_Response.__constants['UPDATE_SUCCESSFULL']

    @property
    def UPDATE_FAILED(self):
        """Message constant 'UPDATE_FAILED'."""
        return Metaclass_UavcanUpdateBattery_Response.__constants['UPDATE_FAILED']


class UavcanUpdateBattery_Response(metaclass=Metaclass_UavcanUpdateBattery_Response):
    """
    Message class 'UavcanUpdateBattery_Response'.

    Constants:
      UPDATE_SUCCESSFULL
      UPDATE_FAILED
    """

    __slots__ = [
        '_success',
    ]

    _fields_and_field_types = {
        'success': 'uint8',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.success = kwargs.get('success', int())

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
        if self.success != other.success:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def success(self):
        """Message field 'success'."""
        return self._success

    @success.setter
    def success(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'success' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'success' field must be an unsigned integer in [0, 255]"
        self._success = value


class Metaclass_UavcanUpdateBattery(type):
    """Metaclass of service 'UavcanUpdateBattery'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('sam_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'sam_msgs.srv.UavcanUpdateBattery')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__uavcan_update_battery

            from sam_msgs.srv import _uavcan_update_battery
            if _uavcan_update_battery.Metaclass_UavcanUpdateBattery_Request._TYPE_SUPPORT is None:
                _uavcan_update_battery.Metaclass_UavcanUpdateBattery_Request.__import_type_support__()
            if _uavcan_update_battery.Metaclass_UavcanUpdateBattery_Response._TYPE_SUPPORT is None:
                _uavcan_update_battery.Metaclass_UavcanUpdateBattery_Response.__import_type_support__()


class UavcanUpdateBattery(metaclass=Metaclass_UavcanUpdateBattery):
    from sam_msgs.srv._uavcan_update_battery import UavcanUpdateBattery_Request as Request
    from sam_msgs.srv._uavcan_update_battery import UavcanUpdateBattery_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
