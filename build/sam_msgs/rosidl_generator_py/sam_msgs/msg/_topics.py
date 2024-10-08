# generated from rosidl_generator_py/resource/_idl.py.em
# with input from sam_msgs:msg/Topics.idl
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
        'VBS_CMD_TOPIC': 'core/vbs_cmd',
        'LCG_CMD_TOPIC': 'core/lcg_cmd',
        'THRUSTER1_CMD_TOPIC': 'core/thruster1_cmd',
        'THRUSTER2_CMD_TOPIC': 'core/thruster2_cmd',
        'THRUST_VECTOR_CMD_TOPIC': 'core/thrust_vector_cmd',
        'DEPTH_TOPIC': 'core/depth20_pressure',
        'DVL_TOPIC': 'core/dvl',
        'LEAK_TOPIC': 'core/leak',
        'VBS_FB_TOPIC': 'core/vbs_fb',
        'LCG_FB_TOPIC': 'core/lcg_fb',
        'THRUSTER1_FB_TOPIC': 'core/thruster1_fb',
        'THRUSTER2_FB_TOPIC': 'core/thruster2_fb',
        'STIM_IMU_TOPIC': 'core/imu',
        'SBG_IMU_TOPIC': 'core/sbg_imu',
        'PRESS_DEPTH20_TOPIC': 'core/depth20_pressure',
        'SIDESCAN_TOPIC': 'payload/sidescan',
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
                'sam_msgs.msg.Topics')
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
            'VBS_CMD_TOPIC': cls.__constants['VBS_CMD_TOPIC'],
            'LCG_CMD_TOPIC': cls.__constants['LCG_CMD_TOPIC'],
            'THRUSTER1_CMD_TOPIC': cls.__constants['THRUSTER1_CMD_TOPIC'],
            'THRUSTER2_CMD_TOPIC': cls.__constants['THRUSTER2_CMD_TOPIC'],
            'THRUST_VECTOR_CMD_TOPIC': cls.__constants['THRUST_VECTOR_CMD_TOPIC'],
            'DEPTH_TOPIC': cls.__constants['DEPTH_TOPIC'],
            'DVL_TOPIC': cls.__constants['DVL_TOPIC'],
            'LEAK_TOPIC': cls.__constants['LEAK_TOPIC'],
            'VBS_FB_TOPIC': cls.__constants['VBS_FB_TOPIC'],
            'LCG_FB_TOPIC': cls.__constants['LCG_FB_TOPIC'],
            'THRUSTER1_FB_TOPIC': cls.__constants['THRUSTER1_FB_TOPIC'],
            'THRUSTER2_FB_TOPIC': cls.__constants['THRUSTER2_FB_TOPIC'],
            'STIM_IMU_TOPIC': cls.__constants['STIM_IMU_TOPIC'],
            'SBG_IMU_TOPIC': cls.__constants['SBG_IMU_TOPIC'],
            'PRESS_DEPTH20_TOPIC': cls.__constants['PRESS_DEPTH20_TOPIC'],
            'SIDESCAN_TOPIC': cls.__constants['SIDESCAN_TOPIC'],
        }

    @property
    def VBS_CMD_TOPIC(self):
        """Message constant 'VBS_CMD_TOPIC'."""
        return Metaclass_Topics.__constants['VBS_CMD_TOPIC']

    @property
    def LCG_CMD_TOPIC(self):
        """Message constant 'LCG_CMD_TOPIC'."""
        return Metaclass_Topics.__constants['LCG_CMD_TOPIC']

    @property
    def THRUSTER1_CMD_TOPIC(self):
        """Message constant 'THRUSTER1_CMD_TOPIC'."""
        return Metaclass_Topics.__constants['THRUSTER1_CMD_TOPIC']

    @property
    def THRUSTER2_CMD_TOPIC(self):
        """Message constant 'THRUSTER2_CMD_TOPIC'."""
        return Metaclass_Topics.__constants['THRUSTER2_CMD_TOPIC']

    @property
    def THRUST_VECTOR_CMD_TOPIC(self):
        """Message constant 'THRUST_VECTOR_CMD_TOPIC'."""
        return Metaclass_Topics.__constants['THRUST_VECTOR_CMD_TOPIC']

    @property
    def DEPTH_TOPIC(self):
        """Message constant 'DEPTH_TOPIC'."""
        return Metaclass_Topics.__constants['DEPTH_TOPIC']

    @property
    def DVL_TOPIC(self):
        """Message constant 'DVL_TOPIC'."""
        return Metaclass_Topics.__constants['DVL_TOPIC']

    @property
    def LEAK_TOPIC(self):
        """Message constant 'LEAK_TOPIC'."""
        return Metaclass_Topics.__constants['LEAK_TOPIC']

    @property
    def VBS_FB_TOPIC(self):
        """Message constant 'VBS_FB_TOPIC'."""
        return Metaclass_Topics.__constants['VBS_FB_TOPIC']

    @property
    def LCG_FB_TOPIC(self):
        """Message constant 'LCG_FB_TOPIC'."""
        return Metaclass_Topics.__constants['LCG_FB_TOPIC']

    @property
    def THRUSTER1_FB_TOPIC(self):
        """Message constant 'THRUSTER1_FB_TOPIC'."""
        return Metaclass_Topics.__constants['THRUSTER1_FB_TOPIC']

    @property
    def THRUSTER2_FB_TOPIC(self):
        """Message constant 'THRUSTER2_FB_TOPIC'."""
        return Metaclass_Topics.__constants['THRUSTER2_FB_TOPIC']

    @property
    def STIM_IMU_TOPIC(self):
        """Message constant 'STIM_IMU_TOPIC'."""
        return Metaclass_Topics.__constants['STIM_IMU_TOPIC']

    @property
    def SBG_IMU_TOPIC(self):
        """Message constant 'SBG_IMU_TOPIC'."""
        return Metaclass_Topics.__constants['SBG_IMU_TOPIC']

    @property
    def PRESS_DEPTH20_TOPIC(self):
        """Message constant 'PRESS_DEPTH20_TOPIC'."""
        return Metaclass_Topics.__constants['PRESS_DEPTH20_TOPIC']

    @property
    def SIDESCAN_TOPIC(self):
        """Message constant 'SIDESCAN_TOPIC'."""
        return Metaclass_Topics.__constants['SIDESCAN_TOPIC']


class Topics(metaclass=Metaclass_Topics):
    """
    Message class 'Topics'.

    Constants:
      VBS_CMD_TOPIC
      LCG_CMD_TOPIC
      THRUSTER1_CMD_TOPIC
      THRUSTER2_CMD_TOPIC
      THRUST_VECTOR_CMD_TOPIC
      DEPTH_TOPIC
      DVL_TOPIC
      LEAK_TOPIC
      VBS_FB_TOPIC
      LCG_FB_TOPIC
      THRUSTER1_FB_TOPIC
      THRUSTER2_FB_TOPIC
      STIM_IMU_TOPIC
      SBG_IMU_TOPIC
      PRESS_DEPTH20_TOPIC
      SIDESCAN_TOPIC
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
