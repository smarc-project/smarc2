cmake_minimum_required(VERSION 3.22)
project(smarc_georef_cpp)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

find_package(ament_cmake REQUIRED)
find_package(ament_cmake_python REQUIRED)
find_package(pybind11_vendor REQUIRED)
find_package(pybind11 REQUIRED)
find_package(rclcpp REQUIRED)
find_package(Python3 REQUIRED COMPONENTS Interpreter Development)
find_package(geographic_msgs REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(tf2 REQUIRED)
find_package(tf2_ros REQUIRED)
find_package(tf2_geometry_msgs REQUIRED)
# Ubuntu's libgeographic(lib)-dev ships a find module here instead of a config file
list(APPEND CMAKE_MODULE_PATH "/usr/share/cmake/geographiclib")
find_package(GeographicLib REQUIRED)

# GeorefUtils library, used by the Python module and exported so other packages can use it
# (see "Usage in C++" in the README)
add_library(${PROJECT_NAME} SHARED
  src/georef_utils.cpp
)
target_include_directories(${PROJECT_NAME} PUBLIC
  $<BUILD_INTERFACE:${CMAKE_CURRENT_SOURCE_DIR}/include>
  $<INSTALL_INTERFACE:include/${PROJECT_NAME}>
)
# GeographicLib is only used in the .cpp, so users of the library don't need it
target_include_directories(${PROJECT_NAME} SYSTEM PRIVATE ${GeographicLib_INCLUDE_DIRS})
target_link_libraries(${PROJECT_NAME} PRIVATE ${GeographicLib_LIBRARIES})
# tf2_geometry_msgs is also only used in the .cpp
target_link_libraries(${PROJECT_NAME} PRIVATE tf2_geometry_msgs::tf2_geometry_msgs)
ament_target_dependencies(${PROJECT_NAME} PUBLIC
  rclcpp
  geographic_msgs
  geometry_msgs
  tf2
  tf2_ros
)

install(
  DIRECTORY include/
  DESTINATION include/${PROJECT_NAME}
)

install(
  TARGETS ${PROJECT_NAME}
  EXPORT export_${PROJECT_NAME}
  ARCHIVE DESTINATION lib
  LIBRARY DESTINATION lib
  RUNTIME DESTINATION bin
)

ament_export_targets(export_${PROJECT_NAME} HAS_LIBRARY_TARGET)
ament_export_dependencies(
  rclcpp
  geographic_msgs
  geometry_msgs
  tf2
  tf2_ros
)

# Python bindings: installs the python package smarc_georef_cpp with the
# compiled _georef_cpp module inside it
ament_python_install_package(${PROJECT_NAME})

pybind11_add_module(_georef_cpp
  src/python_bindings.cpp
)
target_link_libraries(_georef_cpp PRIVATE ${PROJECT_NAME})

install(
  TARGETS _georef_cpp
  DESTINATION "${PYTHON_INSTALL_DIR}/${PROJECT_NAME}"
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
