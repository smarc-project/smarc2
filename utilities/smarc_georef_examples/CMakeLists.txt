cmake_minimum_required(VERSION 3.22)
project(smarc_georef_examples)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(smarc_georef_cpp REQUIRED)
find_package(rclcpp REQUIRED)
find_package(geographic_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)

# C++ example: uses GeorefUtils from the smarc_georef_cpp library
add_executable(georef_example_node
  src/georef_example_node.cpp
)
target_link_libraries(georef_example_node
  smarc_georef_cpp::smarc_georef_cpp
  rclcpp::rclcpp
  ${geographic_msgs_TARGETS}
  ${geometry_msgs_TARGETS}
  tf2::tf2
)

install(
  TARGETS georef_example_node
  DESTINATION lib/${PROJECT_NAME}
)

# Python example: uses the smarc_georef_cpp Python package
install(
  PROGRAMS scripts/georef_example_node.py
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
