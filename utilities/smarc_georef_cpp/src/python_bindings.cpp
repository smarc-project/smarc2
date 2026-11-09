// pybind11 bindings exposing GeorefUtils to Python.
//
// An rclpy node can't be passed to C++, so GeorefUtils is created with an internal rclcpp
// node in its own rclcpp context, independent of any rclpy context in the same process.
// The tf listener receives tf on its own background thread, so the node isn't spun.
// ROS messages are passed to Python as CDR-serialized bytes; the Python wrapper
// (smarc_georef_cpp/__init__.py) turns them into rclpy message objects.

#include <cstring>
#include <memory>
#include <string>
#include <vector>

#include "pybind11/pybind11.h"
#include "pybind11/stl.h"

#include "rclcpp/rclcpp.hpp"
#include "rclcpp/serialization.hpp"
#include "tf2/exceptions.h"

#include "smarc_georef_cpp/georef_utils.hpp"

namespace py = pybind11;

namespace
{

template<typename MsgT>
py::bytes serialize(const MsgT & msg)
{
  rclcpp::Serialization<MsgT> serializer;
  rclcpp::SerializedMessage serialized;
  serializer.serialize_message(&msg, &serialized);
  const auto & rcl_msg = serialized.get_rcl_serialized_message();
  return py::bytes(reinterpret_cast<const char *>(rcl_msg.buffer), rcl_msg.buffer_length);
}

template<typename MsgT>
MsgT deserialize(const std::string & data)
{
  rclcpp::SerializedMessage serialized(data.size());
  auto & rcl_msg = serialized.get_rcl_serialized_message();
  std::memcpy(rcl_msg.buffer, data.data(), data.size());
  rcl_msg.buffer_length = data.size();

  MsgT msg;
  rclcpp::Serialization<MsgT> serializer;
  serializer.deserialize_message(&serialized, &msg);
  return msg;
}

class PyGeorefUtils
{
public:
  explicit PyGeorefUtils(const std::vector<std::string> & ros_args)
  {
    if (!rclcpp::ok()) {
      // Python (and rclpy) own signal handling; don't let rclcpp install its own.
      rclcpp::init(0, nullptr, rclcpp::InitOptions(), rclcpp::SignalHandlerOptions::None);
    }
    rclcpp::NodeOptions options;
    options.arguments(ros_args);
    node_ = std::make_shared<rclcpp::Node>("georef_utils", options);
    georef_ = std::make_unique<GeorefUtils>(node_.get());
  }

  ~PyGeorefUtils()
  {
    shutdown();
  }

  void shutdown()
  {
    // GeorefUtils (and its tf listener thread) must go before the node it uses
    georef_.reset();
    node_.reset();
  }

  py::bytes lookup_transform(
    const std::string & target_frame, const std::string & source_frame, double timeout_sec)
  {
    geometry_msgs::msg::TransformStamped tf;
    {
      // TF lookups may block until timeout; let other Python threads run meanwhile.
      py::gil_scoped_release release;
      tf = checked_georef()->lookup_transform(target_frame, source_frame, timeout_sec);
    }
    return serialize(tf);
  }

  bool can_transform(
    const std::string & target_frame, const std::string & source_frame, double timeout_sec)
  {
    // May block until timeout; let other Python threads run meanwhile.
    py::gil_scoped_release release;
    return checked_georef()->can_transform(target_frame, source_frame, timeout_sec);
  }

  py::bytes geopoint_to_point_stamped(
    const std::string & geopoint, const std::string & target_frame)
  {
    auto geo = deserialize<geographic_msgs::msg::GeoPoint>(geopoint);
    geometry_msgs::msg::PointStamped point;
    {
      py::gil_scoped_release release;
      point = checked_georef()->geopoint_to_point_stamped(geo, target_frame);
    }
    return serialize(point);
  }

  py::bytes point_stamped_to_geopoint(const std::string & point)
  {
    auto point_msg = deserialize<geometry_msgs::msg::PointStamped>(point);
    geographic_msgs::msg::GeoPoint geo;
    {
      py::gil_scoped_release release;
      geo = checked_georef()->point_stamped_to_geopoint(point_msg);
    }
    return serialize(geo);
  }

  std::string get_utm_frame()
  {
    return checked_georef()->get_utm_frame();
  }

  std::string node_name() const
  {
    if (!node_) {
      throw std::runtime_error("GeorefUtils has been shut down");
    }
    return node_->get_fully_qualified_name();
  }

private:
  GeorefUtils * checked_georef() const
  {
    if (!georef_) {
      throw std::runtime_error("GeorefUtils has been shut down");
    }
    return georef_.get();
  }

  std::shared_ptr<rclcpp::Node> node_;
  std::unique_ptr<GeorefUtils> georef_;
};

}  // namespace

PYBIND11_MODULE(_georef_cpp, m)
{
  m.doc() = "Python bindings for smarc_georef_cpp's GeorefUtils";

  py::register_exception<tf2::TransformException>(m, "TransformException", PyExc_RuntimeError);

  py::class_<PyGeorefUtils>(m, "GeorefUtilsCpp")
  .def(py::init<const std::vector<std::string> &>(), py::arg("ros_args") = std::vector<std::string>{})
  .def("shutdown", &PyGeorefUtils::shutdown, py::call_guard<py::gil_scoped_release>())
  .def("node_name", &PyGeorefUtils::node_name)
  .def("get_utm_frame", &PyGeorefUtils::get_utm_frame)
  .def(
    "lookup_transform", &PyGeorefUtils::lookup_transform,
    py::arg("target_frame"), py::arg("source_frame"), py::arg("timeout_sec") = 0.0)
  .def(
    "can_transform", &PyGeorefUtils::can_transform,
    py::arg("target_frame"), py::arg("source_frame"), py::arg("timeout_sec") = 0.0)
  .def(
    "geopoint_to_point_stamped", &PyGeorefUtils::geopoint_to_point_stamped,
    py::arg("geopoint"), py::arg("target_frame") = "")
  .def(
    "point_stamped_to_geopoint", &PyGeorefUtils::point_stamped_to_geopoint,
    py::arg("point"));

  m.def(
    "shutdown_context", []() {
      if (rclcpp::ok()) {
        rclcpp::shutdown();
      }
    }, "Shut down the rclcpp context used by the internal C++ node(s).");
}
