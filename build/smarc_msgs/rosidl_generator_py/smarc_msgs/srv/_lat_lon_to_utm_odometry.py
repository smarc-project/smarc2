# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_msgs:srv/LatLonToUTMOdometry.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_LatLonToUTMOdometry_Request(type):
    """Metaclass of message 'LatLonToUTMOdometry_Request'."""

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
                'smarc_msgs.srv.LatLonToUTMOdometry_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__lat_lon_to_utm_odometry__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__lat_lon_to_utm_odometry__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__lat_lon_to_utm_odometry__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__lat_lon_to_utm_odometry__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__lat_lon_to_utm_odometry__request

            from smarc_msgs.msg import LatLonOdometry
            if LatLonOdometry.__class__._TYPE_SUPPORT is None:
                LatLonOdometry.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class LatLonToUTMOdometry_Request(metaclass=Metaclass_LatLonToUTMOdometry_Request):
    """Message class 'LatLonToUTMOdometry_Request'."""

    __slots__ = [
        '_lat_lon_odom',
    ]

    _fields_and_field_types = {
        'lat_lon_odom': 'smarc_msgs/LatLonOdometry',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['smarc_msgs', 'msg'], 'LatLonOdometry'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from smarc_msgs.msg import LatLonOdometry
        self.lat_lon_odom = kwargs.get('lat_lon_odom', LatLonOdometry())

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
        if self.lat_lon_odom != other.lat_lon_odom:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def lat_lon_odom(self):
        """Message field 'lat_lon_odom'."""
        return self._lat_lon_odom

    @lat_lon_odom.setter
    def lat_lon_odom(self, value):
        if __debug__:
            from smarc_msgs.msg import LatLonOdometry
            assert \
                isinstance(value, LatLonOdometry), \
                "The 'lat_lon_odom' field must be a sub message of type 'LatLonOdometry'"
        self._lat_lon_odom = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_LatLonToUTMOdometry_Response(type):
    """Metaclass of message 'LatLonToUTMOdometry_Response'."""

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
                'smarc_msgs.srv.LatLonToUTMOdometry_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__lat_lon_to_utm_odometry__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__lat_lon_to_utm_odometry__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__lat_lon_to_utm_odometry__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__lat_lon_to_utm_odometry__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__lat_lon_to_utm_odometry__response

            from nav_msgs.msg import Odometry
            if Odometry.__class__._TYPE_SUPPORT is None:
                Odometry.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class LatLonToUTMOdometry_Response(metaclass=Metaclass_LatLonToUTMOdometry_Response):
    """Message class 'LatLonToUTMOdometry_Response'."""

    __slots__ = [
        '_odom',
    ]

    _fields_and_field_types = {
        'odom': 'nav_msgs/Odometry',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['nav_msgs', 'msg'], 'Odometry'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from nav_msgs.msg import Odometry
        self.odom = kwargs.get('odom', Odometry())

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
        if self.odom != other.odom:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def odom(self):
        """Message field 'odom'."""
        return self._odom

    @odom.setter
    def odom(self, value):
        if __debug__:
            from nav_msgs.msg import Odometry
            assert \
                isinstance(value, Odometry), \
                "The 'odom' field must be a sub message of type 'Odometry'"
        self._odom = value


class Metaclass_LatLonToUTMOdometry(type):
    """Metaclass of service 'LatLonToUTMOdometry'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('smarc_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_msgs.srv.LatLonToUTMOdometry')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__lat_lon_to_utm_odometry

            from smarc_msgs.srv import _lat_lon_to_utm_odometry
            if _lat_lon_to_utm_odometry.Metaclass_LatLonToUTMOdometry_Request._TYPE_SUPPORT is None:
                _lat_lon_to_utm_odometry.Metaclass_LatLonToUTMOdometry_Request.__import_type_support__()
            if _lat_lon_to_utm_odometry.Metaclass_LatLonToUTMOdometry_Response._TYPE_SUPPORT is None:
                _lat_lon_to_utm_odometry.Metaclass_LatLonToUTMOdometry_Response.__import_type_support__()


class LatLonToUTMOdometry(metaclass=Metaclass_LatLonToUTMOdometry):
    from smarc_msgs.srv._lat_lon_to_utm_odometry import LatLonToUTMOdometry_Request as Request
    from smarc_msgs.srv._lat_lon_to_utm_odometry import LatLonToUTMOdometry_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
