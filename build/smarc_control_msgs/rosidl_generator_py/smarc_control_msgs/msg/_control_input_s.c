// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smarc_control_msgs:msg/ControlInput.idl
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
#include "smarc_control_msgs/msg/detail/control_input__struct.h"
#include "smarc_control_msgs/msg/detail/control_input__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smarc_control_msgs__msg__control_input__convert_from_py(PyObject * _pymsg, void * _ros_message)
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
    assert(strncmp("smarc_control_msgs.msg._control_input.ControlInput", full_classname_dest, 50) == 0);
  }
  smarc_control_msgs__msg__ControlInput * ros_message = _ros_message;
  {  // thrusterrpm
    PyObject * field = PyObject_GetAttrString(_pymsg, "thrusterrpm");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->thrusterrpm = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // thrustervertical
    PyObject * field = PyObject_GetAttrString(_pymsg, "thrustervertical");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->thrustervertical = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // thrusterhorizontal
    PyObject * field = PyObject_GetAttrString(_pymsg, "thrusterhorizontal");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->thrusterhorizontal = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // vbs
    PyObject * field = PyObject_GetAttrString(_pymsg, "vbs");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->vbs = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // lcg
    PyObject * field = PyObject_GetAttrString(_pymsg, "lcg");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->lcg = PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smarc_control_msgs__msg__control_input__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of ControlInput */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smarc_control_msgs.msg._control_input");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "ControlInput");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smarc_control_msgs__msg__ControlInput * ros_message = (smarc_control_msgs__msg__ControlInput *)raw_ros_message;
  {  // thrusterrpm
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->thrusterrpm);
    {
      int rc = PyObject_SetAttrString(_pymessage, "thrusterrpm", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // thrustervertical
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->thrustervertical);
    {
      int rc = PyObject_SetAttrString(_pymessage, "thrustervertical", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // thrusterhorizontal
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->thrusterhorizontal);
    {
      int rc = PyObject_SetAttrString(_pymessage, "thrusterhorizontal", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // vbs
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->vbs);
    {
      int rc = PyObject_SetAttrString(_pymessage, "vbs", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // lcg
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->lcg);
    {
      int rc = PyObject_SetAttrString(_pymessage, "lcg", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
