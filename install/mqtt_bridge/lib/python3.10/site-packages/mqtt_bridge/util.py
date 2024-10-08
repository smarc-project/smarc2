from importlib import import_module
from typing import Any, Callable, Dict

# does not do lists... replaced with rosidl_runtime_py stuff! 
#from rosbridge_library.internal import message_conversion
from rosidl_runtime_py.set_message import set_message_fields
from rosidl_runtime_py.convert import message_to_ordereddict

def lookup_object(object_path: str, package: str='mqtt_bridge') -> Any:
    """ lookup object from a some.module:object_name specification. """
    module_name, obj_name = object_path.split(":")
    module = import_module(module_name, package)
    obj = getattr(module, obj_name)
    return obj

def populate_instance(msg_dict, msg_type):
    set_message_fields(msg_type, msg_dict)
    return msg_type

def extract_values(msg):
    return message_to_ordereddict(msg)

#extract_values = message_conversion.extract_values  
#populate_instance = message_conversion.populate_instance 

__all__ = ['lookup_object', 'extract_values', 'populate_instance']