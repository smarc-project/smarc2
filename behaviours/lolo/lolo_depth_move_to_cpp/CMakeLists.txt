cmake_minimum_required(VERSION 3.10)
project(lolo_depth_move_to_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(lolo_msgs REQUIRED)
find_package(smarc_msgs REQUIRED)
find_package(smarc_geofence_utils REQUIRED)
find_package(smarc_action_base_cpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(geodesy REQUIRED)
find_package(geographic_msgs REQUIRED)

add_executable(lolo_depth_move_to
  src/lolo_depth_move_to.cpp
)
ament_target_dependencies(lolo_depth_move_to
  rclcpp
  geometry_msgs
  nav_msgs
  lolo_msgs
  smarc_action_base_cpp
  tf2
  tf2_ros
  tf2_geometry_msgs
  geodesy
  geographic_msgs
)

install(
  TARGETS
    lolo_depth_move_to
  DESTINATION lib/${PROJECT_NAME}
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
