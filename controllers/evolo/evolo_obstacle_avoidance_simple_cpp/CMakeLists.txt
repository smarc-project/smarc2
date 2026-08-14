cmake_minimum_required(VERSION 3.8)
project(evolo_obstacle_avoidance_simple_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(nav_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(evolo_msgs REQUIRED)
find_package(smarc_msgs REQUIRED)
find_package(visualization_msgs REQUIRED)

# uncomment the following section in order to fill in
# further dependencies manually.
# find_package(<dependency> REQUIRED)

add_executable(evolo_obstacle_avoidance_cpp src/evolo_obstacle_avoidance_cpp.cpp)

ament_target_dependencies(evolo_obstacle_avoidance_cpp
  rclcpp
  geometry_msgs
  nav_msgs
  std_msgs
  evolo_msgs
  smarc_msgs
  tf2
  tf2_ros
  tf2_geometry_msgs
  visualization_msgs
)

target_include_directories(evolo_obstacle_avoidance_cpp PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include>)
target_compile_features(evolo_obstacle_avoidance_cpp PUBLIC c_std_99 cxx_std_17)  # Require C99 and C++17

install(TARGETS evolo_obstacle_avoidance_cpp
  DESTINATION lib/${PROJECT_NAME})

install(
  DIRECTORY include/
  DESTINATION include
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
