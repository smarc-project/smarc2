cmake_minimum_required(VERSION 3.8)
project(drone_msgs)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# Find necessary dependencies
find_package(ament_cmake REQUIRED)
find_package(rosidl_default_generators REQUIRED)

find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(std_msgs REQUIRED)

# Generate drone-related message and service interfaces
rosidl_generate_interfaces(${PROJECT_NAME}
  "msg/Topics.msg"         # Topics for the drone
  "msg/Links.msg"          #links for drone
                
  DEPENDENCIES geometry_msgs sensor_msgs std_msgs
)

# Add build tests (if testing is enabled)
if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # Skipping linting for copyright and cpplint
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()

