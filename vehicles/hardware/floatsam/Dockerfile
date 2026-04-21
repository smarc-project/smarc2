FROM ros:humble-ros-base-jammy

# Use bash for source commands
SHELL ["/bin/bash", "-c"]

# Environment settings
ENV ROS_DOMAIN_ID=42
ENV ROS_LOCALHOST_ONLY=0
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# 1. Install basics (Added cmake for the XRCE-DDS Agent)
RUN apt update && apt upgrade -y \
 && apt install -y python3-pip apt-utils ros-dev-tools unzip git cmake \
 && pip install --no-input setuptools==58.2.0

# 2. Setup User
ARG UID=1000
ARG GID=1000
ARG USERNAME=smarc2user

RUN adduser --quiet --disabled-password --gecos '' --uid ${UID:=1000} --uid ${GID:=1000} ${USERNAME} \
 && usermod -aG sudo ${USERNAME}

RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

# ---------------------------------------------------------
# NEW: Build the Micro-XRCE-DDS Agent Globally (Outside ROS)
# ---------------------------------------------------------
WORKDIR /opt
RUN git clone https://github.com/eProsima/Micro-XRCE-DDS-Agent.git \
 && cd Micro-XRCE-DDS-Agent \
 && mkdir build && cd build \
 && cmake .. \
 && make \
 && make install \
 && ldconfig /usr/local/lib/

# 3. Prepare Workspace
WORKDIR /home/${USERNAME}/colcon_ws/src

# Clone the PX4 Vocabulary (px4_msgs)
RUN git clone https://github.com/PX4/px4_msgs.git

# Copy your custom smarc2 code
COPY . smarc2/

# Configure colcon defaults
WORKDIR /home/${USERNAME}
RUN mkdir .colcon/ \
 && echo "{ \"build\": { \"symlink-install\": true } }" > .colcon/defaults.yaml

# 4. Install Dependencies
WORKDIR /home/${USERNAME}/colcon_ws/src/smarc2
RUN scripts/get-submodules.sh external_packages

WORKDIR /home/${USERNAME}/colcon_ws

# Split up the commands so we can see exact errors
RUN rosdep update
RUN rosdep install --from-paths src --ignore-src -r -y

RUN source /opt/ros/humble/setup.bash \
 && colcon build

# Setup environment variables and permissions
RUN echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc \
 && echo "source /home/${USERNAME}/colcon_ws/install/setup.bash" >> /home/${USERNAME}/.bashrc \
 && chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# ---------------------------------------------------------
# Create the Entrypoint Script to run the Agent
# ---------------------------------------------------------
RUN echo "#!/bin/bash" > /home/${USERNAME}/entrypoint.sh \
 && echo "set -e" >> /home/${USERNAME}/entrypoint.sh \
 && echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/entrypoint.sh \
 && echo "source /home/${USERNAME}/colcon_ws/install/setup.bash" >> /home/${USERNAME}/entrypoint.sh \
 && echo "echo 'Starting PX4 Micro-XRCE-DDS Agent on UDP port 8888...'" >> /home/${USERNAME}/entrypoint.sh \
 && echo "MicroXRCEAgent udp4 -p 8888 &" >> /home/${USERNAME}/entrypoint.sh \
 && echo 'exec "$@"' >> /home/${USERNAME}/entrypoint.sh \
 && chmod +x /home/${USERNAME}/entrypoint.sh

USER ${USERNAME}

# Set the Entrypoint to our new script
ENTRYPOINT ["/home/smarc2user/entrypoint.sh"]

# Set the default command to bash
CMD ["/bin/bash"]
