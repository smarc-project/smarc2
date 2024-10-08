# generated from rosidl_generator_py/resource/_idl.py.em
# with input from smarc_mission_msgs:action/GotoWaypoint.idl
# generated code does not contain a copyright notice


# Import statements for member types

import builtins  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_GotoWaypoint_Goal(type):
    """Metaclass of message 'GotoWaypoint_Goal'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_Goal')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__goal
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__goal
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__goal
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__goal
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__goal

            from smarc_mission_msgs.msg import GotoWaypoint
            if GotoWaypoint.__class__._TYPE_SUPPORT is None:
                GotoWaypoint.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_Goal(metaclass=Metaclass_GotoWaypoint_Goal):
    """Message class 'GotoWaypoint_Goal'."""

    __slots__ = [
        '_waypoint',
    ]

    _fields_and_field_types = {
        'waypoint': 'smarc_mission_msgs/GotoWaypoint',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['smarc_mission_msgs', 'msg'], 'GotoWaypoint'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from smarc_mission_msgs.msg import GotoWaypoint
        self.waypoint = kwargs.get('waypoint', GotoWaypoint())

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
        if self.waypoint != other.waypoint:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def waypoint(self):
        """Message field 'waypoint'."""
        return self._waypoint

    @waypoint.setter
    def waypoint(self, value):
        if __debug__:
            from smarc_mission_msgs.msg import GotoWaypoint
            assert \
                isinstance(value, GotoWaypoint), \
                "The 'waypoint' field must be a sub message of type 'GotoWaypoint'"
        self._waypoint = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_Result(type):
    """Metaclass of message 'GotoWaypoint_Result'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_Result')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__result
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__result
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__result
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__result
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__result

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_Result(metaclass=Metaclass_GotoWaypoint_Result):
    """Message class 'GotoWaypoint_Result'."""

    __slots__ = [
        '_reached_waypoint',
    ]

    _fields_and_field_types = {
        'reached_waypoint': 'boolean',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.reached_waypoint = kwargs.get('reached_waypoint', bool())

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
        if self.reached_waypoint != other.reached_waypoint:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def reached_waypoint(self):
        """Message field 'reached_waypoint'."""
        return self._reached_waypoint

    @reached_waypoint.setter
    def reached_waypoint(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'reached_waypoint' field must be of type 'bool'"
        self._reached_waypoint = value


# Import statements for member types

# already imported above
# import builtins

import math  # noqa: E402, I100

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_Feedback(type):
    """Metaclass of message 'GotoWaypoint_Feedback'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_Feedback')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__feedback
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__feedback
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__feedback
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__feedback
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__feedback

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_Feedback(metaclass=Metaclass_GotoWaypoint_Feedback):
    """Message class 'GotoWaypoint_Feedback'."""

    __slots__ = [
        '_time_remaining',
        '_feedback_message',
        '_distance_remaining',
    ]

    _fields_and_field_types = {
        'time_remaining': 'builtin_interfaces/Time',
        'feedback_message': 'string',
        'distance_remaining': 'float',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from builtin_interfaces.msg import Time
        self.time_remaining = kwargs.get('time_remaining', Time())
        self.feedback_message = kwargs.get('feedback_message', str())
        self.distance_remaining = kwargs.get('distance_remaining', float())

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
        if self.time_remaining != other.time_remaining:
            return False
        if self.feedback_message != other.feedback_message:
            return False
        if self.distance_remaining != other.distance_remaining:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def time_remaining(self):
        """Message field 'time_remaining'."""
        return self._time_remaining

    @time_remaining.setter
    def time_remaining(self, value):
        if __debug__:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'time_remaining' field must be a sub message of type 'Time'"
        self._time_remaining = value

    @builtins.property
    def feedback_message(self):
        """Message field 'feedback_message'."""
        return self._feedback_message

    @feedback_message.setter
    def feedback_message(self, value):
        if __debug__:
            assert \
                isinstance(value, str), \
                "The 'feedback_message' field must be of type 'str'"
        self._feedback_message = value

    @builtins.property
    def distance_remaining(self):
        """Message field 'distance_remaining'."""
        return self._distance_remaining

    @distance_remaining.setter
    def distance_remaining(self, value):
        if __debug__:
            assert \
                isinstance(value, float), \
                "The 'distance_remaining' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'distance_remaining' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._distance_remaining = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_SendGoal_Request(type):
    """Metaclass of message 'GotoWaypoint_SendGoal_Request'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_SendGoal_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__send_goal__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__send_goal__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__send_goal__request
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__send_goal__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__send_goal__request

            from smarc_mission_msgs.action import GotoWaypoint
            if GotoWaypoint.Goal.__class__._TYPE_SUPPORT is None:
                GotoWaypoint.Goal.__class__.__import_type_support__()

            from unique_identifier_msgs.msg import UUID
            if UUID.__class__._TYPE_SUPPORT is None:
                UUID.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_SendGoal_Request(metaclass=Metaclass_GotoWaypoint_SendGoal_Request):
    """Message class 'GotoWaypoint_SendGoal_Request'."""

    __slots__ = [
        '_goal_id',
        '_goal',
    ]

    _fields_and_field_types = {
        'goal_id': 'unique_identifier_msgs/UUID',
        'goal': 'smarc_mission_msgs/GotoWaypoint_Goal',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['unique_identifier_msgs', 'msg'], 'UUID'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['smarc_mission_msgs', 'action'], 'GotoWaypoint_Goal'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from unique_identifier_msgs.msg import UUID
        self.goal_id = kwargs.get('goal_id', UUID())
        from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Goal
        self.goal = kwargs.get('goal', GotoWaypoint_Goal())

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
        if self.goal_id != other.goal_id:
            return False
        if self.goal != other.goal:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def goal_id(self):
        """Message field 'goal_id'."""
        return self._goal_id

    @goal_id.setter
    def goal_id(self, value):
        if __debug__:
            from unique_identifier_msgs.msg import UUID
            assert \
                isinstance(value, UUID), \
                "The 'goal_id' field must be a sub message of type 'UUID'"
        self._goal_id = value

    @builtins.property
    def goal(self):
        """Message field 'goal'."""
        return self._goal

    @goal.setter
    def goal(self, value):
        if __debug__:
            from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Goal
            assert \
                isinstance(value, GotoWaypoint_Goal), \
                "The 'goal' field must be a sub message of type 'GotoWaypoint_Goal'"
        self._goal = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_SendGoal_Response(type):
    """Metaclass of message 'GotoWaypoint_SendGoal_Response'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_SendGoal_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__send_goal__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__send_goal__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__send_goal__response
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__send_goal__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__send_goal__response

            from builtin_interfaces.msg import Time
            if Time.__class__._TYPE_SUPPORT is None:
                Time.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_SendGoal_Response(metaclass=Metaclass_GotoWaypoint_SendGoal_Response):
    """Message class 'GotoWaypoint_SendGoal_Response'."""

    __slots__ = [
        '_accepted',
        '_stamp',
    ]

    _fields_and_field_types = {
        'accepted': 'boolean',
        'stamp': 'builtin_interfaces/Time',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['builtin_interfaces', 'msg'], 'Time'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.accepted = kwargs.get('accepted', bool())
        from builtin_interfaces.msg import Time
        self.stamp = kwargs.get('stamp', Time())

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
        if self.accepted != other.accepted:
            return False
        if self.stamp != other.stamp:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def accepted(self):
        """Message field 'accepted'."""
        return self._accepted

    @accepted.setter
    def accepted(self, value):
        if __debug__:
            assert \
                isinstance(value, bool), \
                "The 'accepted' field must be of type 'bool'"
        self._accepted = value

    @builtins.property
    def stamp(self):
        """Message field 'stamp'."""
        return self._stamp

    @stamp.setter
    def stamp(self, value):
        if __debug__:
            from builtin_interfaces.msg import Time
            assert \
                isinstance(value, Time), \
                "The 'stamp' field must be a sub message of type 'Time'"
        self._stamp = value


class Metaclass_GotoWaypoint_SendGoal(type):
    """Metaclass of service 'GotoWaypoint_SendGoal'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_SendGoal')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__action__goto_waypoint__send_goal

            from smarc_mission_msgs.action import _goto_waypoint
            if _goto_waypoint.Metaclass_GotoWaypoint_SendGoal_Request._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_SendGoal_Request.__import_type_support__()
            if _goto_waypoint.Metaclass_GotoWaypoint_SendGoal_Response._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_SendGoal_Response.__import_type_support__()


class GotoWaypoint_SendGoal(metaclass=Metaclass_GotoWaypoint_SendGoal):
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_SendGoal_Request as Request
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_SendGoal_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_GetResult_Request(type):
    """Metaclass of message 'GotoWaypoint_GetResult_Request'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_GetResult_Request')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__get_result__request
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__get_result__request
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__get_result__request
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__get_result__request
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__get_result__request

            from unique_identifier_msgs.msg import UUID
            if UUID.__class__._TYPE_SUPPORT is None:
                UUID.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_GetResult_Request(metaclass=Metaclass_GotoWaypoint_GetResult_Request):
    """Message class 'GotoWaypoint_GetResult_Request'."""

    __slots__ = [
        '_goal_id',
    ]

    _fields_and_field_types = {
        'goal_id': 'unique_identifier_msgs/UUID',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['unique_identifier_msgs', 'msg'], 'UUID'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from unique_identifier_msgs.msg import UUID
        self.goal_id = kwargs.get('goal_id', UUID())

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
        if self.goal_id != other.goal_id:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def goal_id(self):
        """Message field 'goal_id'."""
        return self._goal_id

    @goal_id.setter
    def goal_id(self, value):
        if __debug__:
            from unique_identifier_msgs.msg import UUID
            assert \
                isinstance(value, UUID), \
                "The 'goal_id' field must be a sub message of type 'UUID'"
        self._goal_id = value


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_GetResult_Response(type):
    """Metaclass of message 'GotoWaypoint_GetResult_Response'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_GetResult_Response')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__get_result__response
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__get_result__response
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__get_result__response
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__get_result__response
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__get_result__response

            from smarc_mission_msgs.action import GotoWaypoint
            if GotoWaypoint.Result.__class__._TYPE_SUPPORT is None:
                GotoWaypoint.Result.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_GetResult_Response(metaclass=Metaclass_GotoWaypoint_GetResult_Response):
    """Message class 'GotoWaypoint_GetResult_Response'."""

    __slots__ = [
        '_status',
        '_result',
    ]

    _fields_and_field_types = {
        'status': 'int8',
        'result': 'smarc_mission_msgs/GotoWaypoint_Result',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('int8'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['smarc_mission_msgs', 'action'], 'GotoWaypoint_Result'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.status = kwargs.get('status', int())
        from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Result
        self.result = kwargs.get('result', GotoWaypoint_Result())

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
        if self.status != other.status:
            return False
        if self.result != other.result:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def status(self):
        """Message field 'status'."""
        return self._status

    @status.setter
    def status(self, value):
        if __debug__:
            assert \
                isinstance(value, int), \
                "The 'status' field must be of type 'int'"
            assert value >= -128 and value < 128, \
                "The 'status' field must be an integer in [-128, 127]"
        self._status = value

    @builtins.property
    def result(self):
        """Message field 'result'."""
        return self._result

    @result.setter
    def result(self, value):
        if __debug__:
            from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Result
            assert \
                isinstance(value, GotoWaypoint_Result), \
                "The 'result' field must be a sub message of type 'GotoWaypoint_Result'"
        self._result = value


class Metaclass_GotoWaypoint_GetResult(type):
    """Metaclass of service 'GotoWaypoint_GetResult'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_GetResult')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_srv__action__goto_waypoint__get_result

            from smarc_mission_msgs.action import _goto_waypoint
            if _goto_waypoint.Metaclass_GotoWaypoint_GetResult_Request._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_GetResult_Request.__import_type_support__()
            if _goto_waypoint.Metaclass_GotoWaypoint_GetResult_Response._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_GetResult_Response.__import_type_support__()


class GotoWaypoint_GetResult(metaclass=Metaclass_GotoWaypoint_GetResult):
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_GetResult_Request as Request
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_GetResult_Response as Response

    def __init__(self):
        raise NotImplementedError('Service classes can not be instantiated')


# Import statements for member types

# already imported above
# import builtins

# already imported above
# import rosidl_parser.definition


class Metaclass_GotoWaypoint_FeedbackMessage(type):
    """Metaclass of message 'GotoWaypoint_FeedbackMessage'."""

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
                'smarc_mission_msgs.action.GotoWaypoint_FeedbackMessage')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__action__goto_waypoint__feedback_message
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__action__goto_waypoint__feedback_message
            cls._CONVERT_TO_PY = module.convert_to_py_msg__action__goto_waypoint__feedback_message
            cls._TYPE_SUPPORT = module.type_support_msg__action__goto_waypoint__feedback_message
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__action__goto_waypoint__feedback_message

            from smarc_mission_msgs.action import GotoWaypoint
            if GotoWaypoint.Feedback.__class__._TYPE_SUPPORT is None:
                GotoWaypoint.Feedback.__class__.__import_type_support__()

            from unique_identifier_msgs.msg import UUID
            if UUID.__class__._TYPE_SUPPORT is None:
                UUID.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class GotoWaypoint_FeedbackMessage(metaclass=Metaclass_GotoWaypoint_FeedbackMessage):
    """Message class 'GotoWaypoint_FeedbackMessage'."""

    __slots__ = [
        '_goal_id',
        '_feedback',
    ]

    _fields_and_field_types = {
        'goal_id': 'unique_identifier_msgs/UUID',
        'feedback': 'smarc_mission_msgs/GotoWaypoint_Feedback',
    }

    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['unique_identifier_msgs', 'msg'], 'UUID'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['smarc_mission_msgs', 'action'], 'GotoWaypoint_Feedback'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
            'Invalid arguments passed to constructor: %s' % \
            ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        from unique_identifier_msgs.msg import UUID
        self.goal_id = kwargs.get('goal_id', UUID())
        from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Feedback
        self.feedback = kwargs.get('feedback', GotoWaypoint_Feedback())

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
        if self.goal_id != other.goal_id:
            return False
        if self.feedback != other.feedback:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def goal_id(self):
        """Message field 'goal_id'."""
        return self._goal_id

    @goal_id.setter
    def goal_id(self, value):
        if __debug__:
            from unique_identifier_msgs.msg import UUID
            assert \
                isinstance(value, UUID), \
                "The 'goal_id' field must be a sub message of type 'UUID'"
        self._goal_id = value

    @builtins.property
    def feedback(self):
        """Message field 'feedback'."""
        return self._feedback

    @feedback.setter
    def feedback(self, value):
        if __debug__:
            from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Feedback
            assert \
                isinstance(value, GotoWaypoint_Feedback), \
                "The 'feedback' field must be a sub message of type 'GotoWaypoint_Feedback'"
        self._feedback = value


class Metaclass_GotoWaypoint(type):
    """Metaclass of action 'GotoWaypoint'."""

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
                'smarc_mission_msgs.action.GotoWaypoint')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._TYPE_SUPPORT = module.type_support_action__action__goto_waypoint

            from action_msgs.msg import _goal_status_array
            if _goal_status_array.Metaclass_GoalStatusArray._TYPE_SUPPORT is None:
                _goal_status_array.Metaclass_GoalStatusArray.__import_type_support__()
            from action_msgs.srv import _cancel_goal
            if _cancel_goal.Metaclass_CancelGoal._TYPE_SUPPORT is None:
                _cancel_goal.Metaclass_CancelGoal.__import_type_support__()

            from smarc_mission_msgs.action import _goto_waypoint
            if _goto_waypoint.Metaclass_GotoWaypoint_SendGoal._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_SendGoal.__import_type_support__()
            if _goto_waypoint.Metaclass_GotoWaypoint_GetResult._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_GetResult.__import_type_support__()
            if _goto_waypoint.Metaclass_GotoWaypoint_FeedbackMessage._TYPE_SUPPORT is None:
                _goto_waypoint.Metaclass_GotoWaypoint_FeedbackMessage.__import_type_support__()


class GotoWaypoint(metaclass=Metaclass_GotoWaypoint):

    # The goal message defined in the action definition.
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Goal as Goal
    # The result message defined in the action definition.
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Result as Result
    # The feedback message defined in the action definition.
    from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_Feedback as Feedback

    class Impl:

        # The send_goal service using a wrapped version of the goal message as a request.
        from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_SendGoal as SendGoalService
        # The get_result service using a wrapped version of the result message as a response.
        from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_GetResult as GetResultService
        # The feedback message with generic fields which wraps the feedback message.
        from smarc_mission_msgs.action._goto_waypoint import GotoWaypoint_FeedbackMessage as FeedbackMessage

        # The generic service to cancel a goal.
        from action_msgs.srv._cancel_goal import CancelGoal as CancelGoalService
        # The generic message for get the status of a goal.
        from action_msgs.msg._goal_status_array import GoalStatusArray as GoalStatusMessage

    def __init__(self):
        raise NotImplementedError('Action classes can not be instantiated')
