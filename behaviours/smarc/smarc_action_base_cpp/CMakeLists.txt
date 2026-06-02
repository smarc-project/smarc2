cmake_minimum_required(VERSION 3.8)
project(smarc_action_base_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(std_msgs REQUIRED)
find_package(smarc_msgs REQUIRED)
find_package(nlohmann_json REQUIRED)

add_library(gentler_action_server
  src/graceful_shutdown.cpp
  src/gentler_action_server.cpp
)
target_include_directories(gentler_action_server PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>"
)
ament_target_dependencies(gentler_action_server
  rclcpp
  rclcpp_action
  std_msgs
  smarc_msgs
)
target_link_libraries(gentler_action_server
  nlohmann_json::nlohmann_json
)

add_executable(super_simple_action_server_cpp
  src/super_simple_action_server.cpp
)
target_include_directories(super_simple_action_server_cpp PUBLIC
  "$<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>"
  "$<INSTALL_INTERFACE:include>"
)
ament_target_dependencies(super_simple_action_server_cpp
  rclcpp
)
target_link_libraries(super_simple_action_server_cpp
  gentler_action_server
)

install(
  DIRECTORY include/
  DESTINATION include
)

install(
  TARGETS gentler_action_server
  EXPORT export_gentler_action_server
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

install(
  TARGETS super_simple_action_server_cpp
  DESTINATION lib/${PROJECT_NAME}
)

ament_export_targets(export_gentler_action_server HAS_LIBRARY_TARGET)
ament_export_dependencies(
  rclcpp
  rclcpp_action
  std_msgs
  smarc_msgs
  nlohmann_json
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
