#include "smarc_geofence_utils/geofence_path_checker.hpp"

#include <algorithm>
#include <cmath>
#include <vector>

#include "geometry_msgs/msg/point.hpp"
#include "geometry_msgs/msg/point32.hpp"
#include "geometry_msgs/msg/polygon.hpp"

namespace smarc_geofence_utils {
namespace {

struct Point2 {
  double x;
  double y;
};

Point2 to_point2(const geometry_msgs::msg::Point& point) {
  return Point2{point.x, point.y};
}

Point2 to_point2(const geometry_msgs::msg::Point32& point) {
  return Point2{point.x, point.y};
}

double cross(const Point2& a, const Point2& b, const Point2& c) {
  return (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
}

bool point_on_segment(const Point2& point, const Point2& a, const Point2& b) {
  constexpr double kEpsilon = 1e-9;
  if (std::abs(cross(a, b, point)) > kEpsilon) {
    return false;
  }

  return point.x >= std::min(a.x, b.x) - kEpsilon &&
         point.x <= std::max(a.x, b.x) + kEpsilon &&
         point.y >= std::min(a.y, b.y) - kEpsilon &&
         point.y <= std::max(a.y, b.y) + kEpsilon;
}

bool segments_intersect(const Point2& a, const Point2& b, const Point2& c,
                        const Point2& d) {
  constexpr double kEpsilon = 1e-9;
  const double ab_c = cross(a, b, c);
  const double ab_d = cross(a, b, d);
  const double cd_a = cross(c, d, a);
  const double cd_b = cross(c, d, b);

  if (std::abs(ab_c) <= kEpsilon && point_on_segment(c, a, b)) {
    return true;
  }
  if (std::abs(ab_d) <= kEpsilon && point_on_segment(d, a, b)) {
    return true;
  }
  if (std::abs(cd_a) <= kEpsilon && point_on_segment(a, c, d)) {
    return true;
  }
  if (std::abs(cd_b) <= kEpsilon && point_on_segment(b, c, d)) {
    return true;
  }

  return ((ab_c > 0.0 && ab_d < 0.0) ||
          (ab_c < 0.0 && ab_d > 0.0)) &&
         ((cd_a > 0.0 && cd_b < 0.0) ||
          (cd_a < 0.0 && cd_b > 0.0));
}

bool point_inside_polygon(const Point2& point,
                          const geometry_msgs::msg::Polygon& polygon) {
  if (polygon.points.size() < 3) {
    return false;
  }

  bool inside = false;
  for (std::size_t i = 0, j = polygon.points.size() - 1;
       i < polygon.points.size(); j = i++) {
    const auto pi = to_point2(polygon.points[i]);
    const auto pj = to_point2(polygon.points[j]);

    if (point_on_segment(point, pi, pj)) {
      return true;
    }

    const bool edge_crosses_ray =
        ((pi.y > point.y) != (pj.y > point.y)) &&
        (point.x <
         (pj.x - pi.x) * (point.y - pi.y) / (pj.y - pi.y) + pi.x);
    if (edge_crosses_ray) {
      inside = !inside;
    }
  }

  return inside;
}

bool point_inside_any_polygon(
    const Point2& point,
    const std::vector<geometry_msgs::msg::Polygon>& polygons) {
  for (const auto& polygon : polygons) {
    if (point_inside_polygon(point, polygon)) {
      return true;
    }
  }
  return false;
}

bool segment_crosses_polygon_boundary(
    const Point2& a, const Point2& b,
    const geometry_msgs::msg::Polygon& polygon) {
  if (polygon.points.size() < 3) {
    return false;
  }

  for (std::size_t i = 0; i < polygon.points.size(); ++i) {
    const auto c = to_point2(polygon.points[i]);
    const auto d = to_point2(polygon.points[(i + 1) % polygon.points.size()]);
    if (segments_intersect(a, b, c, d)) {
      return true;
    }
  }

  return false;
}

bool segment_crosses_any_polygon_boundary(
    const Point2& a, const Point2& b,
    const std::vector<geometry_msgs::msg::Polygon>& polygons) {
  for (const auto& polygon : polygons) {
    if (segment_crosses_polygon_boundary(a, b, polygon)) {
      return true;
    }
  }
  return false;
}

bool segment_is_contained_by_any_fence(
    const Point2& a, const Point2& b,
    const std::vector<geometry_msgs::msg::Polygon>& fences) {
  for (const auto& fence : fences) {
    if (point_inside_polygon(a, fence) && point_inside_polygon(b, fence) &&
        !segment_crosses_polygon_boundary(a, b, fence)) {
      return true;
    }
  }
  return false;
}

GeofencePathCheckResult unsafe(const std::string& feedback) {
  return GeofencePathCheckResult{false, feedback};
}

}  // namespace

GeofencePathCheckResult check_path_against_geofence(
    const nav_msgs::msg::Path& path,
    const smarc_msgs::msg::GeofencePolygonsStamped& geofence_polygons) {
  if (geofence_polygons.header.frame_id.empty()) {
    return unsafe("GEOFENCE_POLYGONS_MISSING_FRAME");
  }

  if (path.header.frame_id != geofence_polygons.header.frame_id) {
    return unsafe("GEOFENCE_PATH_FRAME_MISMATCH");
  }

  if (geofence_polygons.geofence.empty()) {
    return unsafe("GEOFENCE_POLYGONS_EMPTY");
  }

  for (const auto& fence : geofence_polygons.geofence) {
    if (fence.points.size() < 3) {
      return unsafe("GEOFENCE_POLYGON_INVALID");
    }
  }

  for (const auto& island : geofence_polygons.islands) {
    if (!island.points.empty() && island.points.size() < 3) {
      return unsafe("GEOFENCE_ISLAND_INVALID");
    }
  }

  for (const auto& pose : path.poses) {
    const auto point = to_point2(pose.pose.position);
    if (!point_inside_any_polygon(point, geofence_polygons.geofence)) {
      return unsafe("GEOFENCE_PATH_POINT_OUTSIDE");
    }

    if (point_inside_any_polygon(point, geofence_polygons.islands)) {
      return unsafe("GEOFENCE_PATH_POINT_INSIDE_ISLAND");
    }
  }

  for (std::size_t i = 1; i < path.poses.size(); ++i) {
    const auto a = to_point2(path.poses[i - 1].pose.position);
    const auto b = to_point2(path.poses[i].pose.position);
    if (!segment_is_contained_by_any_fence(a, b, geofence_polygons.geofence)) {
      return unsafe("GEOFENCE_PATH_SEGMENT_CROSSES_FENCE");
    }

    if (segment_crosses_any_polygon_boundary(a, b, geofence_polygons.islands)) {
      return unsafe("GEOFENCE_PATH_SEGMENT_CROSSES_ISLAND");
    }
  }

  return GeofencePathCheckResult{true, "GEOFENCE_PATH_SAFE"};
}

}  // namespace smarc_geofence_utils
