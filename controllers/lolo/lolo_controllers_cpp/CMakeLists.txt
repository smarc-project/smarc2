cmake_minimum_required(VERSION 3.8)
project(lolo_controllers_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(lolo_msgs REQUIRED)
find_package(smarc_msgs REQUIRED)
find_package(diagnostic_msgs REQUIRED)
find_package(diagnostic_updater REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)


include_directories(
  ${PROJECT_SOURCE_DIR}/lib/
)

set (PID_SRC
  lib/pid/Pid.cpp
)

add_executable(lolo_controllers
  src/lolo_controllers.cpp
  ${PID_SRC}
)

ament_target_dependencies(lolo_controllers
  rclcpp
  geometry_msgs
  nav_msgs
  std_msgs
  lolo_msgs
  smarc_msgs
  diagnostic_msgs
  diagnostic_updater
  tf2
  tf2_ros
  tf2_geometry_msgs
)

install(
  TARGETS
  lolo_controllers
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY launch
  DESTINATION share/${PROJECT_NAME}
)

install(
  FILES README.md
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
