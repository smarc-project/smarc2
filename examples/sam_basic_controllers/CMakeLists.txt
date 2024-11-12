cmake_minimum_required(VERSION 3.8)
project(sam_basic_controllers)

if(NOT CMAKE_CXX_STANDARD)
  set(CMAKE_CXX_STANDARD 17)
endif()
if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find_package(<dependency> REQUIRED)
# use this for mixed cpp-py packages like this one...
# or maybe just dont mix them lol
find_package(ament_cmake_python REQUIRED)

find_package(rclcpp REQUIRED)
find_package(rclpy REQUIRED)
find_package(sam_msgs REQUIRED)
find_package(std_msgs REQUIRED)
find_package(smarc_msgs REQUIRED)



add_executable(pid_actuator_trim src/pid_utils/pid_actuator_trim.cpp)

# ament package dependencies. Most ROS stuff.
# use target_link_libraries for stuff like Boost...
ament_target_dependencies(pid_actuator_trim
  rclcpp
  std_msgs
  sam_msgs
  smarc_msgs)


install(
  TARGETS pid_actuator_trim
  DESTINATION lib/${PROJECT_NAME}
)

# simple python exectuables
# dont forget a __init__.py!
ament_python_install_package(${PROJECT_NAME})
install(
  PROGRAMS
  ${PROJECT_NAME}/depth_lookahead_node.py
  ${PROJECT_NAME}/thruster_ctrl_node.py
  DESTINATION lib/${PROJECT_NAME}
)

install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch/
)


# When there is such a directory...
# install(
#   DIRECTORY include/
#   DESTINATION share/${PROJECT_NAME}/include/
# )

ament_package()
