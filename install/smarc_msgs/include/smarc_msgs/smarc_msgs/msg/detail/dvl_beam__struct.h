// generated from rosidl_generator_c/resource/idl__struct.h.em
// with input from smarc_msgs:msg/DVLBeam.idl
// generated code does not contain a copyright notice

#ifndef SMARC_MSGS__MSG__DETAIL__DVL_BEAM__STRUCT_H_
#define SMARC_MSGS__MSG__DETAIL__DVL_BEAM__STRUCT_H_

#ifdef __cplusplus
extern "C"
{
#endif

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>


// Constants defined in the message

// Include directives for member types
// Member 'pose'
#include "geometry_msgs/msg/detail/pose_stamped__struct.h"

/// Struct defined in msg/DVLBeam in the package smarc_msgs.
/**
  * Copyright (c) 2016 The UUV Simulator Authors.
  * All rights reserved.
  *
  * Licensed under the Apache License, Version 2.0 (the "License");
  * you may not use this file except in compliance with the License.
  * You may obtain a copy of the License at
  *
  *     http://www.apache.org/licenses/LICENSE-2.0
  *
  * Unless required by applicable law or agreed to in writing, software
  * distributed under the License is distributed on an "AS IS" BASIS,
  * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
  * See the License for the specific language governing permissions and
  * limitations under the License.
 */
typedef struct smarc_msgs__msg__DVLBeam
{
  /// measured range or < 0 if invalid
  double range;
  double range_covariance;
  /// measured velocity of corr. beam
  double velocity;
  double velocity_covariance;
  /// Beam link pose wrt DVL link frame
  geometry_msgs__msg__PoseStamped pose;
} smarc_msgs__msg__DVLBeam;

// Struct for a sequence of smarc_msgs__msg__DVLBeam.
typedef struct smarc_msgs__msg__DVLBeam__Sequence
{
  smarc_msgs__msg__DVLBeam * data;
  /// The number of valid items in data
  size_t size;
  /// The number of allocated items in data
  size_t capacity;
} smarc_msgs__msg__DVLBeam__Sequence;

#ifdef __cplusplus
}
#endif

#endif  // SMARC_MSGS__MSG__DETAIL__DVL_BEAM__STRUCT_H_
