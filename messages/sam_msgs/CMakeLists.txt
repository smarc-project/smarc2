cmake_minimum_required(VERSION 3.8)
project(sam_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find_package(<dependency> REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/ArrayCommand.msg"
  "msg/BallastAngles.msg"
  "msg/CircuitStatus.msg"
  "msg/CircuitStatusStampedArray.msg"
  "msg/CircuitStatusStamped.msg"
  "msg/Command.msg"
  "msg/ConsumedChargeArray.msg"
  "msg/ConsumedChargeFeedback.msg"
  "msg/ConsumedCharge.msg"
  "msg/CTP.msg"
  "msg/LightCommandArray.msg"
  "msg/LightCommand.msg"
  "msg/PercentStamped.msg"
  "msg/ThrusterAngles.msg"
  "msg/ThrusterRPMs.msg"
  "msg/UavcanNodeStatus.msg"
  "msg/UavcanNodeStatusNamedArray.msg"
  "msg/UavcanNodeStatusNamed.msg"
  "msg/Topics.msg"
  "msg/Links.msg"
  "msg/JoyButtons.msg"
  "srv/UavcanUpdateBattery.srv"
  "action/SystemsCheck.action"
  DEPENDENCIES geometry_msgs sensor_msgs std_msgs
 )

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
