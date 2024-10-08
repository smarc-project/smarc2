// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smarc_msgs:msg/DualThrusterRPM.idl
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
#include "smarc_msgs/msg/detail/dual_thruster_rpm__struct.h"
#include "smarc_msgs/msg/detail/dual_thruster_rpm__functions.h"

bool smarc_msgs__msg__thruster_rpm__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * smarc_msgs__msg__thruster_rpm__convert_to_py(void * raw_ros_message);
bool smarc_msgs__msg__thruster_rpm__convert_from_py(PyObject * _pymsg, void * _ros_message);
PyObject * smarc_msgs__msg__thruster_rpm__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool smarc_msgs__msg__dual_thruster_rpm__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[50];
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
    assert(strncmp("smarc_msgs.msg._dual_thruster_rpm.DualThrusterRPM", full_classname_dest, 49) == 0);
  }
  smarc_msgs__msg__DualThrusterRPM * ros_message = _ros_message;
  {  // thruster_front
    PyObject * field = PyObject_GetAttrString(_pymsg, "thruster_front");
    if (!field) {
      return false;
    }
    if (!smarc_msgs__msg__thruster_rpm__convert_from_py(field, &ros_message->thruster_front)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // thruster_back
    PyObject * field = PyObject_GetAttrString(_pymsg, "thruster_back");
    if (!field) {
      return false;
    }
    if (!smarc_msgs__msg__thruster_rpm__convert_from_py(field, &ros_message->thruster_back)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smarc_msgs__msg__dual_thruster_rpm__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of DualThrusterRPM */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smarc_msgs.msg._dual_thruster_rpm");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "DualThrusterRPM");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smarc_msgs__msg__DualThrusterRPM * ros_message = (smarc_msgs__msg__DualThrusterRPM *)raw_ros_message;
  {  // thruster_front
    PyObject * field = NULL;
    field = smarc_msgs__msg__thruster_rpm__convert_to_py(&ros_message->thruster_front);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "thruster_front", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // thruster_back
    PyObject * field = NULL;
    field = smarc_msgs__msg__thruster_rpm__convert_to_py(&ros_message->thruster_back);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "thruster_back", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
