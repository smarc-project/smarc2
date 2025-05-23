<!--toc:start-->
- [go_to_geopoint](#gotogeopoint)
- [Implementing an Action Server/Client](#implementing-an-action-serverclient)
  - [Creating an Action](#creating-an-action)
    - [ROS2 Humble Doc's](#ros2-humble-docs)
  - [Implementing with smarc-action-base](#implementing-with-smarc-action-base)
    - [Server](#server)
    - [Client](#client)
  - [ROS2 Humble Documentation on Action Server Client](#ros2-humble-documentation-on-action-server-client)
<!--toc:end-->

# go_to_geopoint

Non-trivial example implementation of action client and action server with `smarc_action_base`. 

# Implementing an Action Server/Client

## Creating an Action

Action server/client's utilize custom ROS2 message types to communicate. This message consists of three items:
- Goal
- Feedback 
- Result

These concepts are easy to google and read in the docs so to not avoid duplication a starting point is provided below

### ROS2 Humble Doc's
- [What are Actions?](https://docs.ros.org/en/humble/Concepts/Basic/About-Actions.html) 
- [Creating an Action](https://docs.ros.org/en/humble/Tutorials/Intermediate/Creating-an-Action.html) 

## Implementing with smarc-action-base

### Server
In order to implement a server using the provided framework the following functions must be filled out:

- `goal_callback`
    - The action server needs to manage what goals it accepts and rejects. This is handled in this callback. To see how to formulate the response such that ROS understand consult the docstring on the `goal_callback` or the example.
    - Default behavior is to reject any incoming goal requests if there is a current active goal (this is part of the base class and is not controlled by the receiver)
- `cancel_callback`
    - The action server needs to manage how it cancels goals. This is handled in this callback. This may seem trivial, but imagine a simple case where the action server is moving an AUV to a new waypoint and the client requests to cancel. The action server needs to stop the AUV's motion and indicate whether or not that was successful to the client. This is exactly the purpose of this callback.
    To see how to formulate the response such that ROS understand consult the docstring on the `cancel_callback` or the example.
- `execution_callback`
    - The execution callback is simpler than the previous examples. This is simply the callback where the user parses the Goal message and does what it needs to do with it to begin the action. Additionally feedback can be provided here by the action server to the client if the action takes a significant amount of time to complete.
    - Ensure that in the execution callback and feedback loop you are checking is `is_valid_goal` as goal cancellation in ROS does not kill your execution callback.

### Client
In order to implement a client using the provided framework the following functions must be filled out:

- `feedback_callback`
- `goal_response_callback`
- `result_callback`

These are much simpler to understand than the server version above. The client must manage `ACCEPT` or `REJECT` goal requests via the `goal_response_callback`. Feedback can be parsed, logged, or dealt with in any manner through the `feedback_callback`. Finally, the success of the action is provided and can be parsed and used for other actions, servers, topics, etc in the `result_callback`.

**WARNING** If the action server does not accept the goal, there will be no feedback or response as it was rejected.


## ROS2 Humble Documentation on Action Server Client
This simple action-server-client tutorial provides the basis of what an action server-client is 
- [ROS2 Tutorial](https://docs.ros.org/en/humble/Tutorials/Intermediate/Writing-an-Action-Server-Client/Py.html) 

