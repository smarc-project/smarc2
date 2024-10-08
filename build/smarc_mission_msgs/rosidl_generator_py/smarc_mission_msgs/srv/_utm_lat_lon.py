# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:srv/UTMLatLon.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_UTMLatLon_Request(type):
    """Metaclass of message 'UTMLatLon_Request'."""

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
            module = import_type_support('smarc_mission_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_mission_msgs.srv.UTMLatLon_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__utm_lat_lon__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__utm_lat_lon__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__utm_lat_lon__request
            cls._TYPE_SUPPORT = module.type_support_msg__srv__utm_lat_lon__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__utm_lat_lon__request

            from geographic_msgs.msg import GeoPoint
            if GeoPoint.__class__._TYPE_SUPPORT is None:
                GeoPoint.__class__.__import_type_support__()

            from geometry_msgs.msg import PointStamped
            if PointStamped.__class__._TYPE_SUPPORT is None:
                PointStamped.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class UTMLatLon_Request(metaclass=Metaclass_UTMLatLon_Request):
    """Message class 'UTMLatLon_Request'."""

    __slots__ = [
        '_utm_points',
        '_lat_lon_points',
    ]

    _fields_and_field_types = {
        'utm_points': 'sequence<geometry_msgs/PointStamped>',
        'lat_lon_points': 'sequence<geographic_msgs/GeoPoint>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'PointStamped')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geographic_msgs', 'msg'], 'GeoPoint')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.utm_points = kwargs.get('utm_points', [])
        self.lat_lon_points = kwargs.get('lat_lon_points', [])

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
        if self.utm_points != other.utm_points:
            return False
        if self.lat_lon_points != other.lat_lon_points:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def utm_points(self):
        """Message field 'utm_points'."""
        return self._utm_points

    @utm_points.setter
    def utm_points(self, value):
        if __debug__:
            from geometry_msgs.msg import PointStamped
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, PointStamped) for v in value) and
                 True), \
                "The 'utm_points' field must be a set or sequence and each value of type 'PointStamped'"
        self._utm_points = value

    @builtins.property
    def lat_lon_points(self):
        """Message field 'lat_lon_points'."""
        return self._lat_lon_points

    @lat_lon_points.setter
    def lat_lon_points(self, value):
        if __debug__:
            from geographic_msgs.msg import GeoPoint
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, GeoPoint) for v in value) and
                 True), \
                "The 'lat_lon_points' field must be a set or sequence and each value of type 'GeoPoint'"
        self._lat_lon_points = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_UTMLatLon_Response(type):
    """Metaclass of message 'UTMLatLon_Response'."""

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
            module = import_type_support('smarc_mission_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_mission_msgs.srv.UTMLatLon_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__srv__utm_lat_lon__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__srv__utm_lat_lon__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__srv__utm_lat_lon__response
            cls._TYPE_SUPPORT = module.type_support_msg__srv__utm_lat_lon__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__srv__utm_lat_lon__response

            from geographic_msgs.msg import GeoPoint
            if GeoPoint.__class__._TYPE_SUPPORT is None:
                GeoPoint.__class__.__import_type_support__()

            from geometry_msgs.msg import PointStamped
            if PointStamped.__class__._TYPE_SUPPORT is None:
                PointStamped.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class UTMLatLon_Response(metaclass=Metaclass_UTMLatLon_Response):
    """Message class 'UTMLatLon_Response'."""

    __slots__ = [
        '_lat_lon_points',
        '_utm_points',
    ]

    _fields_and_field_types = {
        'lat_lon_points': 'sequence<geographic_msgs/GeoPoint>',
        'utm_points': 'sequence<geometry_msgs/PointStamped>',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geographic_msgs', 'msg'], 'GeoPoint')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['geometry_msgs', 'msg'], 'PointStamped')),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.lat_lon_points = kwargs.get('lat_lon_points', [])
        self.utm_points = kwargs.get('utm_points', [])

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
        if self.lat_lon_points != other.lat_lon_points:
            return False
        if self.utm_points != other.utm_points:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def lat_lon_points(self):
        """Message field 'lat_lon_points'."""
        return self._lat_lon_points

    @lat_lon_points.setter
    def lat_lon_points(self, value):
        if __debug__:
            from geographic_msgs.msg import GeoPoint
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, GeoPoint) for v in value) and
                 True), \
                "The 'lat_lon_points' field must be a set or sequence and each value of type 'GeoPoint'"
        self._lat_lon_points = value

    @builtins.property
    def utm_points(self):
        """Message field 'utm_points'."""
        return self._utm_points

    @utm_points.setter
    def utm_points(self, value):
        if __debug__:
            from geometry_msgs.msg import PointStamped
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, PointStamped) for v in value) and
                 True), \
                "The 'utm_points' field must be a set or sequence and each value of type 'PointStamped'"
        self._utm_points = value


class Metaclass_UTMLatLon(type):
    """Metaclass of service 'UTMLatLon'."""

    _TYPE_SUPPORT = None

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('smarc_mission_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'smarc_mission_msgs.srv.UTMLatLon')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__srv__utm_lat_lon

            from smarc_mission_msgs.srv import _utm_lat_lon
            if _utm_lat_lon.Metaclass_UTMLatLon_Request._TYPE_SUPPORT is None:
                _utm_lat_lon.Metaclass_UTMLatLon_Request.__import_type_support__()
            if _utm_lat_lon.Metaclass_UTMLatLon_Response._TYPE_SUPPORT is None:
                _utm_lat_lon.Metaclass_UTMLatLon_Response.__import_type_support__()


class UTMLatLon(metaclass=Metaclass_UTMLatLon):
    from smarc_mission_msgs.srv._utm_lat_lon import UTMLatLon_Request as Request
    from smarc_mission_msgs.srv._utm_lat_lon import UTMLatLon_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')
