cmake_minimum_required(VERSION 3.8)
project(sam_description)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find_package(<dependency> REQUIRED)
find_package(ament_cmake REQUIRED)

install(
  DIRECTORY launch/
  DESTINATION share/${PROJECT_NAME}/launch/
)

install(
  DIRECTORY mesh/
  DESTINATION share/${PROJECT_NAME}/mesh/
)

install(
  DIRECTORY robots/
  DESTINATION share/${PROJECT_NAME}/robots/
)

install(
  DIRECTORY urdf/
  DESTINATION share/${PROJECT_NAME}/urdf/
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