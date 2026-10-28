#pragma once

#include <algorithm>
#include <optional>

class PID
{
public:
  
  PID(double kP, double kI, double kD, double max_output);

  PID(double kP = 0.0, double kI = 0.0, double kD = 0.0, double max_output = 0, double max_integral = 0);

  void reset();

  double update_error(double error, double time_s);

  // Setters so gains can be changed at runtime (e.g. from ROS parameters)
  void set_gains(double kP, double kI, double kD);
  void set_cutoff_frequency(double f_cut);

  //for diagnostic
  double get_p_gain() {return kP_; };
  double get_i_gain() {return kI_; };
  double get_d_gain() {return kD_; };
  double get_p_component() {return std::clamp(last_proportional_, -max_output_, max_output_); };
  double get_i_component() {return integral_; };
  double get_d_component() {return last_derivative_; };
  double get_last_output() {return last_output_; };

private:
  static constexpr double kPi = 3.14159265358979323846;

  double kP_;
  double kI_;
  double kD_;
  double max_output_;
  double max_integral_;

  double integral_;
  double last_update_;
  double last_error_;
  double last_derivative_;
  double last_proportional_;
  double last_output_;
  double f_cut_;
};