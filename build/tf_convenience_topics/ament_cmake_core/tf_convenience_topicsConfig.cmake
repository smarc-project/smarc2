# generated from ament/cmake/core/templates/nameConfig.cmake.in

# prevent multiple inclusion
if(_tf_convenience_topics_CONFIG_INCLUDED)
  # ensure to keep the found flag the same
  if(NOT DEFINED tf_convenience_topics_FOUND)
    # explicitly set it to FALSE, otherwise CMake will set it to TRUE
    set(tf_convenience_topics_FOUND FALSE)
  elseif(NOT tf_convenience_topics_FOUND)
    # use separate condition to avoid uninitialized variable warning
    set(tf_convenience_topics_FOUND FALSE)
  endif()
  return()
endif()
set(_tf_convenience_topics_CONFIG_INCLUDED TRUE)

# output package information
if(NOT tf_convenience_topics_FIND_QUIETLY)
  message(STATUS "Found tf_convenience_topics: 0.0.0 (${tf_convenience_topics_DIR})")
endif()

# warn when using a deprecated package
if(NOT "" STREQUAL "")
  set(_msg "Package 'tf_convenience_topics' is deprecated")
  # append custom deprecation text if available
  if(NOT "" STREQUAL "TRUE")
    set(_msg "${_msg} ()")
  endif()
  # optionally quiet the deprecation message
  if(NOT ${tf_convenience_topics_DEPRECATED_QUIET})
    message(DEPRECATION "${_msg}")
  endif()
endif()

# flag package as ament-based to distinguish it after being find_package()-ed
set(tf_convenience_topics_FOUND_AMENT_PACKAGE TRUE)

# include all config extra files
set(_extras "")
foreach(_extra ${_extras})
  include("${tf_convenience_topics_DIR}/${_extra}")
endforeach()
