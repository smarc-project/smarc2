# Messages

All the messages, actions, services should live here.  
It might make sense to split and group messages depending on their use cases, such as "for bt", "for sam" etc.


## `Topics.msg`
Use `Topics.msg` in context-specific (vehicle, package, repo...) message packages to define your list of topics.
Use these strings when creating subs/pubs instead of defining all of the topics in every node as parameters that rarely (if ever) change.
If a topic is actually intended to be changed on launch, you can still define that as a parameter, with the defaul value coming from the Topics message.

> For string constants, use single quotes. Like so: `string THING = 'some words'`.


### Why?
No more "I thought it was `rpm_1`, so it is `rpm1`?" kind of problems!

This reduces duplicate and unneeded parameters and strings that can lead to "stupid" errors. 
This way, if two nodes share a topic (literally the point of a topic) we can be certain that they are using the same string without thinking about it.
This is a common design for basically all multi-author software.

See [sam_msgs.msg::Topics](./sam_msgs/msg/Topics.msg) and [this example node](../examples/ros2_python_examples/ros2_python_examples/sam_view.py).

This also makes it very easy for IDEs to auto-suggest you the topics~

## drone_msgs
Message definitions specific to Drone.

Contains drone-specific topics.

## sam_msgs
Message definitions specific to SAM AUV.

Contains sam-specific topics.

## smarc_mission_msgs
Messages that concern planning, global things like lat/lon/utm, behaviour tree-related functions...


## smarc_msgs
Message definitions that don't belong anywhere else.

Contains vehicle-agnostic topics.
