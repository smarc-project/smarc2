cmake_minimum_required(VERSION 3.8)
project(smarc_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find_package(<dependency> REQUIRED)
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(geometry_msgs REQUIRED)
find_package(geographic_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(builtin_interfaces REQUIRED)

rosidl_generate_interfaces(${PROJECT_NAME}
  "srv/CellOccupied.srv"
  "srv/AddTask.srv"
  "srv/AddTasks.srv"
  "srv/NEDENURotation.srv"
  "srv/LatLonToUTMOdometry.srv"
  "msg/CommsMessage.msg"
  "msg/ControllerStatus.msg"
  "msg/CTD.msg"
  "msg/DualThrusterFeedback.msg"
  "msg/DualThrusterRPM.msg"
  "msg/DVLBeam.msg"
  "msg/DVL.msg"
  "msg/FloatStamped.msg"
  "msg/LatLonOdometry.msg"
  "msg/LatLonStamped.msg"
  "msg/Leak.msg"
  "msg/PercentStamped.msg"
  "msg/SensorStatus.msg"
  "msg/Sidescan.msg"
  "msg/SMTask.msg"
  "msg/StringArray.msg"
  "msg/ThrusterDC.msg"
  "msg/ThrusterFeedback.msg"
  "msg/ThrusterRPM.msg"
  "msg/Topics.msg"
  "msg/StringStamped.msg"
  DEPENDENCIES geometry_msgs geographic_msgs nav_msgs sensor_msgs std_msgs builtin_interfaces
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
