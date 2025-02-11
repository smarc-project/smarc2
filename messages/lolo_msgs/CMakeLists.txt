cmake_minimum_required(VERSION 3.8)
project(lolo_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find_package(<dependency> REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

# These were just copied from sam_msgs
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# Add messages here!!
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/BottomTrack.msg"
  "msg/CaptainService.msg"
  "msg/CustomCommand.msg"
  "msg/HyperionFluorescence.msg"
  "msg/HyperionTurbidity.msg"
  "msg/JfeDo.msg"
  "msg/Pd0BottomTrack.msg"
  "msg/Pd0FixedLeader.msg"
  "msg/Pd0VariableLeader.msg"
  "msg/Pressures.msg"
  "msg/RbrCtd.msg"
  "msg/Status.msg"
  "msg/Temperatures.msg"
  "msg/UsblTopsideCorrection.msg"
  "msg/VbsMode.msg"
  "msg/VbsTank.msg"
  "msg/VescFeedback.msg"
  "msg/VolzServo.msg"
  "msg/Topics.msg"
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
