# generated from rosidl_generator_py/resource/_idl.py.em
# with input from dead_reckoning_msgs:msg/Topics.idl
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
        'DR_ODOM_TOPIC': 'dr/odom',
        'DR_DEPTH_POSE_TOPIC': 'dr/depth_pose',
        'DR_GPS_ODOM_TOPIC': 'dr/gps_odom',
        'DR_ROLL_TOPIC': 'dr/roll',
        'DR_PITCH_TOPIC': 'dr/pitch',
        'DR_YAW_TOPIC': 'dr/yaw',
        'DR_DEPTH_TOPIC': 'dr/depth',
        'DR_COMPASS_HEADING_TOPIC': 'dr/compass_heading',
        'DR_LAT_LON_TOPIC': 'dr/lat_lon',
        'DR_ODOM_X_TOPIC': 'dr/x',
        'DR_ODOM_Y_TOPIC': 'dr/y',
        'DR_ODOM_Z_TOPIC': 'dr/z',
        'DR_ODOM_U_TOPIC': 'dr/u',
        'DR_ODOM_V_TOPIC': 'dr/v',
        'DR_ODOM_W_TOPIC': 'dr/w',
        'DR_ODOM_P_TOPIC': 'dr/p',
        'DR_ODOM_Q_TOPIC': 'dr/q',
        'DR_ODOM_R_TOPIC': 'dr/r',
        'DR_ODOM_ALT_TOPIC': 'dr/alt',
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('dead_reckoning_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'dead_reckoning_msgs.msg.Topics')
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
            'DR_ODOM_TOPIC': cls.__constants['DR_ODOM_TOPIC'],
            'DR_DEPTH_POSE_TOPIC': cls.__constants['DR_DEPTH_POSE_TOPIC'],
            'DR_GPS_ODOM_TOPIC': cls.__constants['DR_GPS_ODOM_TOPIC'],
            'DR_ROLL_TOPIC': cls.__constants['DR_ROLL_TOPIC'],
            'DR_PITCH_TOPIC': cls.__constants['DR_PITCH_TOPIC'],
            'DR_YAW_TOPIC': cls.__constants['DR_YAW_TOPIC'],
            'DR_DEPTH_TOPIC': cls.__constants['DR_DEPTH_TOPIC'],
            'DR_COMPASS_HEADING_TOPIC': cls.__constants['DR_COMPASS_HEADING_TOPIC'],
            'DR_LAT_LON_TOPIC': cls.__constants['DR_LAT_LON_TOPIC'],
            'DR_ODOM_X_TOPIC': cls.__constants['DR_ODOM_X_TOPIC'],
            'DR_ODOM_Y_TOPIC': cls.__constants['DR_ODOM_Y_TOPIC'],
            'DR_ODOM_Z_TOPIC': cls.__constants['DR_ODOM_Z_TOPIC'],
            'DR_ODOM_U_TOPIC': cls.__constants['DR_ODOM_U_TOPIC'],
            'DR_ODOM_V_TOPIC': cls.__constants['DR_ODOM_V_TOPIC'],
            'DR_ODOM_W_TOPIC': cls.__constants['DR_ODOM_W_TOPIC'],
            'DR_ODOM_P_TOPIC': cls.__constants['DR_ODOM_P_TOPIC'],
            'DR_ODOM_Q_TOPIC': cls.__constants['DR_ODOM_Q_TOPIC'],
            'DR_ODOM_R_TOPIC': cls.__constants['DR_ODOM_R_TOPIC'],
            'DR_ODOM_ALT_TOPIC': cls.__constants['DR_ODOM_ALT_TOPIC'],
        }

    @property
    def DR_ODOM_TOPIC(self):
        """Message constant 'DR_ODOM_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_TOPIC']

    @property
    def DR_DEPTH_POSE_TOPIC(self):
        """Message constant 'DR_DEPTH_POSE_TOPIC'."""
        return Metaclass_Topics.__constants['DR_DEPTH_POSE_TOPIC']

    @property
    def DR_GPS_ODOM_TOPIC(self):
        """Message constant 'DR_GPS_ODOM_TOPIC'."""
        return Metaclass_Topics.__constants['DR_GPS_ODOM_TOPIC']

    @property
    def DR_ROLL_TOPIC(self):
        """Message constant 'DR_ROLL_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ROLL_TOPIC']

    @property
    def DR_PITCH_TOPIC(self):
        """Message constant 'DR_PITCH_TOPIC'."""
        return Metaclass_Topics.__constants['DR_PITCH_TOPIC']

    @property
    def DR_YAW_TOPIC(self):
        """Message constant 'DR_YAW_TOPIC'."""
        return Metaclass_Topics.__constants['DR_YAW_TOPIC']

    @property
    def DR_DEPTH_TOPIC(self):
        """Message constant 'DR_DEPTH_TOPIC'."""
        return Metaclass_Topics.__constants['DR_DEPTH_TOPIC']

    @property
    def DR_COMPASS_HEADING_TOPIC(self):
        """Message constant 'DR_COMPASS_HEADING_TOPIC'."""
        return Metaclass_Topics.__constants['DR_COMPASS_HEADING_TOPIC']

    @property
    def DR_LAT_LON_TOPIC(self):
        """Message constant 'DR_LAT_LON_TOPIC'."""
        return Metaclass_Topics.__constants['DR_LAT_LON_TOPIC']

    @property
    def DR_ODOM_X_TOPIC(self):
        """Message constant 'DR_ODOM_X_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_X_TOPIC']

    @property
    def DR_ODOM_Y_TOPIC(self):
        """Message constant 'DR_ODOM_Y_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_Y_TOPIC']

    @property
    def DR_ODOM_Z_TOPIC(self):
        """Message constant 'DR_ODOM_Z_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_Z_TOPIC']

    @property
    def DR_ODOM_U_TOPIC(self):
        """Message constant 'DR_ODOM_U_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_U_TOPIC']

    @property
    def DR_ODOM_V_TOPIC(self):
        """Message constant 'DR_ODOM_V_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_V_TOPIC']

    @property
    def DR_ODOM_W_TOPIC(self):
        """Message constant 'DR_ODOM_W_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_W_TOPIC']

    @property
    def DR_ODOM_P_TOPIC(self):
        """Message constant 'DR_ODOM_P_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_P_TOPIC']

    @property
    def DR_ODOM_Q_TOPIC(self):
        """Message constant 'DR_ODOM_Q_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_Q_TOPIC']

    @property
    def DR_ODOM_R_TOPIC(self):
        """Message constant 'DR_ODOM_R_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_R_TOPIC']

    @property
    def DR_ODOM_ALT_TOPIC(self):
        """Message constant 'DR_ODOM_ALT_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_ALT_TOPIC']


class Topics(metaclass=Metaclass_Topics):
    """
    Message class 'Topics'.

    Constants:
      DR_ODOM_TOPIC
      DR_DEPTH_POSE_TOPIC
      DR_GPS_ODOM_TOPIC
      DR_ROLL_TOPIC
      DR_PITCH_TOPIC
      DR_YAW_TOPIC
      DR_DEPTH_TOPIC
      DR_COMPASS_HEADING_TOPIC
      DR_LAT_LON_TOPIC
      DR_ODOM_X_TOPIC
      DR_ODOM_Y_TOPIC
      DR_ODOM_Z_TOPIC
      DR_ODOM_U_TOPIC
      DR_ODOM_V_TOPIC
      DR_ODOM_W_TOPIC
      DR_ODOM_P_TOPIC
      DR_ODOM_Q_TOPIC
      DR_ODOM_R_TOPIC
      DR_ODOM_ALT_TOPIC
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
