// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from smarc_msgs:msg/Leak.idl
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
#include "smarc_msgs/msg/detail/leak__struct.h"
#include "smarc_msgs/msg/detail/leak__functions.h"


ROSIDL_GENERATOR_C_EXPORT
bool smarc_msgs__msg__leak__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[26];
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
    assert(strncmp("smarc_msgs.msg._leak.Leak", full_classname_dest, 25) == 0);
  }
  smarc_msgs__msg__Leak * ros_message = _ros_message;
  {  // value
    PyObject * field = PyObject_GetAttrString(_pymsg, "value");
    if (!field) {
      return false;
    }
    assert(PyBool_Check(field));
    ros_message->value = (Py_True == field);
    Py_DECREF(field);
  }
  {  // leak_counter
    PyObject * field = PyObject_GetAttrString(_pymsg, "leak_counter");
    if (!field) {
      return false;
    }
    assert(PyLong_Check(field));
    ros_message->leak_counter = (int32_t)PyLong_AsLong(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * smarc_msgs__msg__leak__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of Leak */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("smarc_msgs.msg._leak");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "Leak");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  smarc_msgs__msg__Leak * ros_message = (smarc_msgs__msg__Leak *)raw_ros_message;
  {  // value
    PyObject * field = NULL;
    field = PyBool_FromLong(ros_message->value ? 1 : 0);
    {
      int rc = PyObject_SetAttrString(_pymessage, "value", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // leak_counter
    PyObject * field = NULL;
    field = PyLong_FromLong(ros_message->leak_counter);
    {
      int rc = PyObject_SetAttrString(_pymessage, "leak_counter", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
