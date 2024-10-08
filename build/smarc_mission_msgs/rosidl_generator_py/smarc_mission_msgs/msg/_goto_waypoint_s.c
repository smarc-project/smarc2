// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smarc_mission_msgs:msg/GotoWaypoint.idl
// generated code does not contain a copyright notice
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION
#include <Python.h>
#include <stdbool.h>
#ifndef _WIN32
# pragma GCC diagnostic push
# pragma GCC diagnostic ignored "-Wunused-function"
#endif
#include "numpy/ndarrayobject.h"
#ifndef _WIN32
# pragma GCC diagnostic pop
#endif
#include "rosidl_runtime_c/visibility_control.h"
#include "smarc_mission_msgs/msg/detail/goto_waypoint__struct.h"
#include "smarc_mission_msgs/msg/detail/goto_waypoint__functions.h"

#include "rosidl_runtime_c/string.h"
#include "rosidl_runtime_c/string_functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool geometry_msgs__msg__pose_stamped__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * geometry_msgs__msg__pose_stamped__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool smarc_mission_msgs__msg__goto_waypoint__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[51];
    {
      char * class_name = NULL;
      char * module_name = NULL;
      {
        PyObject * class_attr = PyObject_GetAttrString(_pymsg, "__class__");
        if (class_attr) {
          PyObject * name_attr = PyObject_GetAttrString(class_attr, "__name__");
          if (name_attr) {
            class_name = (char *)PyUnicode_1BYTE_DATA(name_attr);
            Py_DECREF(name_attr);
          }
          PyObject * module_attr = PyObject_GetAttrString(class_attr, "__module__");
          if (module_attr) {
            module_name = (char *)PyUnicode_1BYTE_DATA(module_attr);
            Py_DECREF(module_attr);
          }
          Py_DECREF(class_attr);
        }
      }
      if (!class_name || !module_name) {
        return false;
      }
      snprintf(full_classname_dest, sizeof(full_classname_dest), "%s.%s", module_name, class_name);
    }
    assert(strncmp("smarc_mission_msgs.msg._goto_waypoint.GotoWaypoint", full_classname_dest, 50) == 0);
  }
  smarc_mission_msgs__msg__GotoWaypoint * ros_message = _ros_message;
  {  // pose
    PyObject * field = PyObject_GetAttrString(_pymsg, "pose");
    if (!field) {
      return false;
    }
    if (!geometry_msgs__msg__pose_stamped__convert_from_py(field, &ros_message->pose)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // goal_tolerance
    PyObject * field = PyObject_GetAttrString(_pymsg, "goal_tolerance");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->goal_tolerance = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // z_control_mode
    PyObject * field = PyObject_GetAttrString(_pymsg, "z_control_mode");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->z_control_mode = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // travel_altitude
    PyObject * field = PyObject_GetAttrString(_pymsg, "travel_altitude");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->travel_altitude = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // travel_depth
    PyObject * field = PyObject_GetAttrString(_pymsg, "travel_depth");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->travel_depth = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // speed_control_mode
    PyObject * field = PyObject_GetAttrString(_pymsg, "speed_control_mode");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->speed_control_mode = (uint8_t)PyLong_AsUnsignedLong(field);
    Py_DECREF(field);
  }
  {  // travel_rpm
    PyObject * field = PyObject_GetAttrString(_pymsg, "travel_rpm");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->travel_rpm = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // travel_speed
    PyObject * field = PyObject_GetAttrString(_pymsg, "travel_speed");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->travel_speed = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // lat
    PyObject * field = PyObject_GetAttrString(_pymsg, "lat");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->lat = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // lon
    PyObject * field = PyObject_GetAttrString(_pymsg, "lon");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->lon = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // arrival_heading
    PyObject * field = PyObject_GetAttrString(_pymsg, "arrival_heading");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->arrival_heading = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // use_heading
    PyObject * field = PyObject_GetAttrString(_pymsg, "use_heading");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->use_heading = (Py_True == field);
    Py_DECREF(field);
  }
  {  // name
    PyObject * field = PyObject_GetAttrString(_pymsg, "name");
    if (!field) {
      return false;
    }
    assert(PyUnicode_Check(field));
    PyObject * encoded_field = PyUnicode_AsUTF8String(field);
    if (!encoded_field) {
      Py_DECREF(field);
      return false;
    }
    rosidl_runtime_c__String__assign(&ros_message->name, PyBytes_AS_STRING(encoded_field));
    Py_DECREF(encoded_field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smarc_mission_msgs__msg__goto_waypoint__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of GotoWaypoint */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smarc_mission_msgs.msg._goto_waypoint");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "GotoWaypoint");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smarc_mission_msgs__msg__GotoWaypoint * ros_message = (smarc_mission_msgs__msg__GotoWaypoint *)raw_ros_message;
  {  // pose
    PyObject * field = NULL;
    field = geometry_msgs__msg__pose_stamped__convert_to_py(&ros_message->pose);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "pose", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // goal_tolerance
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->goal_tolerance);
    {
      int rc = PyObject_SetAttrString(_pymessage, "goal_tolerance", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // z_control_mode
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->z_control_mode);
    {
      int rc = PyObject_SetAttrString(_pymessage, "z_control_mode", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // travel_altitude
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->travel_altitude);
    {
      int rc = PyObject_SetAttrString(_pymessage, "travel_altitude", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // travel_depth
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->travel_depth);
    {
      int rc = PyObject_SetAttrString(_pymessage, "travel_depth", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // speed_control_mode
    PyObject * field = NULL;
    field = PyLong_FromUnsignedLong(ros_message->speed_control_mode);
    {
      int rc = PyObject_SetAttrString(_pymessage, "speed_control_mode", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // travel_rpm
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->travel_rpm);
    {
      int rc = PyObject_SetAttrString(_pymessage, "travel_rpm", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // travel_speed
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->travel_speed);
    {
      int rc = PyObject_SetAttrString(_pymessage, "travel_speed", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // lat
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->lat);
    {
      int rc = PyObject_SetAttrString(_pymessage, "lat", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // lon
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->lon);
    {
      int rc = PyObject_SetAttrString(_pymessage, "lon", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // arrival_heading
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->arrival_heading);
    {
      int rc = PyObject_SetAttrString(_pymessage, "arrival_heading", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // use_heading
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->use_heading ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "use_heading", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // name
    PyObject * field = NULL;
    field = PyUnicode_DecodeUTF8(
      ros_message->name.data,
      strlen(ros_message->name.data),
      "replace");
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "name", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
