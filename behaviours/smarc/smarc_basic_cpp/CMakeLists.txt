cmake_minimum_required(VERSION 3.8)
project(smarc_basic_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(smarc_action_base_cpp REQUIRED)

add_executable(wait_action_cpp
  src/wait_action.cpp
)
ament_target_dependencies(wait_action_cpp
  rclcpp
  smarc_action_base_cpp
)

install(
  TARGETS wait_action_cpp
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
