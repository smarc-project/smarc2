#pragma once

#include <string>

#include "nav_msgs/msg/path.hpp"
#include "smarc_msgs/msg/geofence_polygons_stamped.hpp"

namespace smarc_geofence_utils {

struct GeofencePathCheckResult {
  bool safe = false;
  std::string feedback;
};

GeofencePathCheckResult check_path_against_geofence(
    const nav_msgs::msg::Path& path,
    const smarc_msgs::msg::GeofencePolygonsStamped& geofence_polygons);

}  // namespace smarc_geofence_utils
