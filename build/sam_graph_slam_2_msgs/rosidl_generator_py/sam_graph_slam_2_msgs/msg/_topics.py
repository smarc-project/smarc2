# generated from rosidl_generator_py/resource/_idl.py.em
# with input from sam_graph_slam_2_msgs:msg/Topics.idl
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
        'MAP_LINE_DEPTH_TOPIC': 'map/line_depth',
        'MAP_POINT_FEATURE_TOPIC': 'map/point_features',
        'MAP_LINE_FEATURE_TOPIC': 'map/line_features',
        'MAP_MARKED_LINE_SPHERES_TOPIC': 'map/marked_lines_spheres',
        'MAP_MARKED_LINE_LINES_TOPIC': 'map/marked_lines_lines',
        'DETECTOR_HYPOTH_TOPIC': 'payload/sidescan/detection_hypothesis',
        'DETECTOR_MARKER_TOPIC': 'payload/sidescan/detection_markers',
        'DETECTOR_RAW_SSS_TOPIC': 'payload/sidescan/image',
        'DETECTOR_MARKED_SSS_TOPIC': 'payload/sidescan/detection_hypothesis_image',
        'DR_ODOM_TOPIC': 'graph_dr/dr_odom',
        'GT_ODOM_TOPIC': 'graph_dr/gt_odom',
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('sam_graph_slam_2_msgs')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'sam_graph_slam_2_msgs.msg.Topics')
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
            'MAP_LINE_DEPTH_TOPIC': cls.__constants['MAP_LINE_DEPTH_TOPIC'],
            'MAP_POINT_FEATURE_TOPIC': cls.__constants['MAP_POINT_FEATURE_TOPIC'],
            'MAP_LINE_FEATURE_TOPIC': cls.__constants['MAP_LINE_FEATURE_TOPIC'],
            'MAP_MARKED_LINE_SPHERES_TOPIC': cls.__constants['MAP_MARKED_LINE_SPHERES_TOPIC'],
            'MAP_MARKED_LINE_LINES_TOPIC': cls.__constants['MAP_MARKED_LINE_LINES_TOPIC'],
            'DETECTOR_HYPOTH_TOPIC': cls.__constants['DETECTOR_HYPOTH_TOPIC'],
            'DETECTOR_MARKER_TOPIC': cls.__constants['DETECTOR_MARKER_TOPIC'],
            'DETECTOR_RAW_SSS_TOPIC': cls.__constants['DETECTOR_RAW_SSS_TOPIC'],
            'DETECTOR_MARKED_SSS_TOPIC': cls.__constants['DETECTOR_MARKED_SSS_TOPIC'],
            'DR_ODOM_TOPIC': cls.__constants['DR_ODOM_TOPIC'],
            'GT_ODOM_TOPIC': cls.__constants['GT_ODOM_TOPIC'],
        }

    @property
    def MAP_LINE_DEPTH_TOPIC(self):
        """Message constant 'MAP_LINE_DEPTH_TOPIC'."""
        return Metaclass_Topics.__constants['MAP_LINE_DEPTH_TOPIC']

    @property
    def MAP_POINT_FEATURE_TOPIC(self):
        """Message constant 'MAP_POINT_FEATURE_TOPIC'."""
        return Metaclass_Topics.__constants['MAP_POINT_FEATURE_TOPIC']

    @property
    def MAP_LINE_FEATURE_TOPIC(self):
        """Message constant 'MAP_LINE_FEATURE_TOPIC'."""
        return Metaclass_Topics.__constants['MAP_LINE_FEATURE_TOPIC']

    @property
    def MAP_MARKED_LINE_SPHERES_TOPIC(self):
        """Message constant 'MAP_MARKED_LINE_SPHERES_TOPIC'."""
        return Metaclass_Topics.__constants['MAP_MARKED_LINE_SPHERES_TOPIC']

    @property
    def MAP_MARKED_LINE_LINES_TOPIC(self):
        """Message constant 'MAP_MARKED_LINE_LINES_TOPIC'."""
        return Metaclass_Topics.__constants['MAP_MARKED_LINE_LINES_TOPIC']

    @property
    def DETECTOR_HYPOTH_TOPIC(self):
        """Message constant 'DETECTOR_HYPOTH_TOPIC'."""
        return Metaclass_Topics.__constants['DETECTOR_HYPOTH_TOPIC']

    @property
    def DETECTOR_MARKER_TOPIC(self):
        """Message constant 'DETECTOR_MARKER_TOPIC'."""
        return Metaclass_Topics.__constants['DETECTOR_MARKER_TOPIC']

    @property
    def DETECTOR_RAW_SSS_TOPIC(self):
        """Message constant 'DETECTOR_RAW_SSS_TOPIC'."""
        return Metaclass_Topics.__constants['DETECTOR_RAW_SSS_TOPIC']

    @property
    def DETECTOR_MARKED_SSS_TOPIC(self):
        """Message constant 'DETECTOR_MARKED_SSS_TOPIC'."""
        return Metaclass_Topics.__constants['DETECTOR_MARKED_SSS_TOPIC']

    @property
    def DR_ODOM_TOPIC(self):
        """Message constant 'DR_ODOM_TOPIC'."""
        return Metaclass_Topics.__constants['DR_ODOM_TOPIC']

    @property
    def GT_ODOM_TOPIC(self):
        """Message constant 'GT_ODOM_TOPIC'."""
        return Metaclass_Topics.__constants['GT_ODOM_TOPIC']


class Topics(metaclass=Metaclass_Topics):
    """
    Message class 'Topics'.

    Constants:
      MAP_LINE_DEPTH_TOPIC
      MAP_POINT_FEATURE_TOPIC
      MAP_LINE_FEATURE_TOPIC
      MAP_MARKED_LINE_SPHERES_TOPIC
      MAP_MARKED_LINE_LINES_TOPIC
      DETECTOR_HYPOTH_TOPIC
      DETECTOR_MARKER_TOPIC
      DETECTOR_RAW_SSS_TOPIC
      DETECTOR_MARKED_SSS_TOPIC
      DR_ODOM_TOPIC
      GT_ODOM_TOPIC
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
