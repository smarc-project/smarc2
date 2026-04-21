FROM ros:humble-ros-base-jammy

# Use bash for source commands
SHELL ["/bin/bash", "-c"]

# Environment settings
ENV ROS_DOMAIN_ID=42
ENV ROS_LOCALHOST_ONLY=0
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# 1. Install basics
RUN apt update && apt upgrade -y \
    && apt install -y python3-pip apt-utils ros-dev-tools unzip git \
    && pip install --no-input setuptools==58.2.0

# 2. Setup User
ARG UID=1000
ARG GID=1000
ARG USERNAME=smarc2user
RUN adduser --quiet --disabled-password --gecos '' --uid ${UID:=1000} --uid ${GID:=1000} ${USERNAME} \
    && usermod -aG sudo ${USERNAME}
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/${USERNAME}

# 3. Prepare Workspace
RUN mkdir -p colcon_ws/src/smarc2
COPY . colcon_ws/src/smarc2/

# Configure colcon defaults
RUN mkdir .colcon/ \
    && echo "{ \"build\": { \"symlink-install\": true } }" > .colcon/defaults.yaml

# 4. Install Dependencies & Build
WORKDIR /home/${USERNAME}/colcon_ws/src/smarc2
# This script automatically downloads ROS-TCP-Endpoint, so we don't need to clone it manually
RUN scripts/get-submodules.sh external_packages

WORKDIR /home/${USERNAME}/colcon_ws
# Update rosdep and install dependencies
# --ignore-src tells it to look at the downloaded submodules instead of trying to apt-install them
RUN rosdep update \
    && rosdep install --from-paths src --ignore-src -r -y \
    && source /opt/ros/humble/setup.bash \
    && colcon build \
    && echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc \
    && echo "source /home/${USERNAME}/colcon_ws/install/setup.bash" >> /home/${USERNAME}/.bashrc \
    && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

USER ${USERNAME}
ENTRYPOINT ["/bin/bash"]
