cmake_minimum_required(VERSION 3.8)
project(prox_ops_actions)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(evolo_msgs REQUIRED)
find_package(smarc_msgs REQUIRED)
find_package(smarc_geofence_utils REQUIRED)
find_package(smarc_action_base_cpp REQUIRED)

add_executable(evolo_target_intercept
  src/evolo_target_intercept.cpp
)
ament_target_dependencies(evolo_target_intercept
  rclcpp
  geometry_msgs
  nav_msgs
  std_msgs
  evolo_msgs
  smarc_msgs
  smarc_geofence_utils
  smarc_action_base_cpp
)

add_executable(evolo_target_inspect
  src/evolo_target_inspect.cpp
)
ament_target_dependencies(evolo_target_inspect
  rclcpp
  geometry_msgs
  nav_msgs
  evolo_msgs
  smarc_action_base_cpp
)

add_executable(evolo_loiter_patrol
  src/evolo_loiter_patrol.cpp
)
ament_target_dependencies(evolo_loiter_patrol
  rclcpp
  rclcpp_action
  smarc_msgs
  smarc_action_base_cpp
)

add_executable(fake_prox_ops_backend
  src/fake_prox_ops_backend.cpp
)
ament_target_dependencies(fake_prox_ops_backend
  rclcpp
  geometry_msgs
  nav_msgs
  std_msgs
  evolo_msgs
)

install(
  TARGETS
    evolo_target_intercept
    evolo_target_inspect
    evolo_loiter_patrol
    fake_prox_ops_backend
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
