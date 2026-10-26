#include "Pid.h"

//Same max integral as max output
PID::PID(double kP, double kI, double kD, double max_output) {
    PID(kP, kI, kD, max_output, max_output);
}

PID::PID(double kP, double kI, double kD, double max_output, double max_integral)
{
    kP_ = kP;
    kI_ = kI;
    kD_ = kD;
    max_output_ = max_output;
    max_integral_ = max_integral;
    integral_ = 0;
    last_update_ = 0;
    last_error_ = 0;
    last_derivative_ = 0;
    f_cut_ = 20;

}

void PID::reset()
{
    integral_ = 0.0;
    last_update_ = 0;
    last_error_ = 0;
    last_derivative_ = 0;
    last_proportional_ = 0;
}

double PID::update_error(double error, double time_s)
{
    double dt = time_s - last_update_;
    last_update_ = time_s;
    
    // Reset I (and the derivative filter) if dt > 1 s
    bool compute_derivative = true;
    if (dt > 1.0) {
        //Reset integral
        integral_ = 0.0;
        //Reset derivative filter
        compute_derivative = false;
    }

    //Proportional component
    const double proportional = kP_ * error;

    //Only update integral if dt smaller than 1s
    if (dt < 1.0) {
        integral_ += dt * kI_ * error;
    }

    double derivative = 0.0;
    if (dt > 0.0 && compute_derivative) {
        derivative = kD_ * (error - last_error_) / dt;

        // Discrete low-pass filter, cuts out the
        // high-frequency noise that can drive the controller crazy
        const double rc = 1.0 / (2.0 * kPi * f_cut_);
        derivative = last_derivative_ + ((dt / (rc + dt)) * (derivative - last_derivative_));
    }

    // Prevent integral windup
    integral_ = std::clamp(integral_, -max_integral_, max_integral_);

    const double output = proportional + integral_ + derivative;

    last_proportional_ = proportional;
    last_derivative_ = derivative;
    last_update_ = time_s;
    last_error_ = error;

    return std::clamp(output, -max_output_, max_output_);
}


void PID::set_gains(double kP, double kI, double kD) {kP_ = kP; kI_ = kI; kD_ = kD;}
void PID::set_cutoff_frequency(double f_cut) {f_cut_ = f_cut;}