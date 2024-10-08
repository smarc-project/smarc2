// generated from rosidl_generator_py/resource/_idl_support.c.em
// with input from sam_msgs:msg/ConsumedChargeFeedback.idl
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
#include "sam_msgs/msg/detail/consumed_charge_feedback__struct.h"
#include "sam_msgs/msg/detail/consumed_charge_feedback__functions.h"

ROSIDL_GENERATOR_C_IMPORT
bool std_msgs__msg__header__convert_from_py(PyObject * _pymsg, void * _ros_message);
ROSIDL_GENERATOR_C_IMPORT
PyObject * std_msgs__msg__header__convert_to_py(void * raw_ros_message);

ROSIDL_GENERATOR_C_EXPORT
bool sam_msgs__msg__consumed_charge_feedback__convert_from_py(PyObject * _pymsg, void * _ros_message)
{
  // check that the passed message is of the expected Python class
  {
    char full_classname_dest[62];
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
    assert(strncmp("sam_msgs.msg._consumed_charge_feedback.ConsumedChargeFeedback", full_classname_dest, 61) == 0);
  }
  sam_msgs__msg__ConsumedChargeFeedback * ros_message = _ros_message;
  {  // header
    PyObject * field = PyObject_GetAttrString(_pymsg, "header");
    if (!field) {
      return false;
    }
    if (!std_msgs__msg__header__convert_from_py(field, &ros_message->header)) {
      Py_DECREF(field);
      return false;
    }
    Py_DECREF(field);
  }
  {  // main
    PyObject * field = PyObject_GetAttrString(_pymsg, "main");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->main = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // esc1
    PyObject * field = PyObject_GetAttrString(_pymsg, "esc1");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->esc1 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // esc2
    PyObject * field = PyObject_GetAttrString(_pymsg, "esc2");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->esc2 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // esc3
    PyObject * field = PyObject_GetAttrString(_pymsg, "esc3");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->esc3 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v20
    PyObject * field = PyObject_GetAttrString(_pymsg, "v20");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v20 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v12
    PyObject * field = PyObject_GetAttrString(_pymsg, "v12");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v12 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v7
    PyObject * field = PyObject_GetAttrString(_pymsg, "v7");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v7 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v5
    PyObject * field = PyObject_GetAttrString(_pymsg, "v5");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v5 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }
  {  // v33
    PyObject * field = PyObject_GetAttrString(_pymsg, "v33");
    if (!field) {
      return false;
    }
    assert(PyFloat_Check(field));
    ros_message->v33 = (float)PyFloat_AS_DOUBLE(field);
    Py_DECREF(field);
  }

  return true;
}

ROSIDL_GENERATOR_C_EXPORT
PyObject * sam_msgs__msg__consumed_charge_feedback__convert_to_py(void * raw_ros_message)
{
  /* NOTE(esteve): Call constructor of ConsumedChargeFeedback */
  PyObject * _pymessage = NULL;
  {
    PyObject * pymessage_module = PyImport_ImportModule("sam_msgs.msg._consumed_charge_feedback");
    assert(pymessage_module);
    PyObject * pymessage_class = PyObject_GetAttrString(pymessage_module, "ConsumedChargeFeedback");
    assert(pymessage_class);
    Py_DECREF(pymessage_module);
    _pymessage = PyObject_CallObject(pymessage_class, NULL);
    Py_DECREF(pymessage_class);
    if (!_pymessage) {
      return NULL;
    }
  }
  sam_msgs__msg__ConsumedChargeFeedback * ros_message = (sam_msgs__msg__ConsumedChargeFeedback *)raw_ros_message;
  {  // header
    PyObject * field = NULL;
    field = std_msgs__msg__header__convert_to_py(&ros_message->header);
    if (!field) {
      return NULL;
    }
    {
      int rc = PyObject_SetAttrString(_pymessage, "header", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // main
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->main);
    {
      int rc = PyObject_SetAttrString(_pymessage, "main", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // esc1
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->esc1);
    {
      int rc = PyObject_SetAttrString(_pymessage, "esc1", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // esc2
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->esc2);
    {
      int rc = PyObject_SetAttrString(_pymessage, "esc2", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // esc3
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->esc3);
    {
      int rc = PyObject_SetAttrString(_pymessage, "esc3", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v20
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v20);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v20", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v12
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v12);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v12", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v7
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v7);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v7", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v5
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v5);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v5", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }
  {  // v33
    PyObject * field = NULL;
    field = PyFloat_FromDouble(ros_message->v33);
    {
      int rc = PyObject_SetAttrString(_pymessage, "v33", field);
      Py_DECREF(field);
      if (rc) {
        return NULL;
      }
    }
  }

  // ownership of _pymessage is transferred to the caller
  return _pymessage;
}
