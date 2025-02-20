FROM ros:humble-ros-base-jammy

# we want the familiar bash for everything, not sh.
# this makes source-ing work
SHELL ["/bin/bash", "-c"]

# this allows the containers to connect to the host ros2
# use --network=host --ipc=host --pid=host with run 
# and export ROS_DOMAIN_ID=42 on the host
ENV ROS_DOMAIN_ID 42
ENV ROS_LOCALHOST_ONLY 0
ENV RMW_IMPLEMENTATION=rmw_fastrtps_cpp

# update things
RUN apt-get update && apt-get upgrade -y \
    && apt-get install -y python3-pip \
    apt-utils \
    ros-dev-tools \
    unzip \
    vim nano \
    sudo git \
    && pip install --upgrade pip==25.0 \
    && pip install --no-input setuptools==58.2.0 \
    && rm -rf /var/lib/apt/lists/*

# create a non-root user for most things, including ros2
# use --build-arg UID=${id -u} etc to transfer host ids/name into the container!
ARG UID=1000
ARG GID=1000
ARG USERNAME=smarc2user
RUN adduser --quiet --disabled-password --gecos '' --uid ${UID:=1000} --uid ${GID:=1000} ${USERNAME} \
&& usermod -aG sudo ${USERNAME}

# Allow the user to use sudo without a password
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/${USERNAME}

# clone the base smarc2 dir and make the colcon ws while at it
RUN mkdir colcon_ws

# make colcon behave by adding this defaults file
COPY defaults.yaml .colcon/defaults.yaml

WORKDIR /home/${USERNAME}/colcon_ws/src/smarc2

# get the submodules needed for core
RUN scripts/get-submodules.sh external_packages
# get the latest compiled binary of the unity sim
# RUN mkdir -p simulation/binaries \
# &&  cd simulation/binaries \
# &&  ../../scripts/get_latest_unity_standard.sh
# Disabled until we actually have tests that use this stuff

# install deps
WORKDIR /home/${USERNAME}/colcon_ws
RUN rosdep update \
&&  ./src/smarc2/scripts/rosdep_install_from_src.sh \
# no bashrc in dockerfiles, so we source and build in the same run
&&  source /opt/ros/humble/setup.bash \
&&  colcon build \
# add the source directives into the users bashrc
&&  echo "source /opt/ros/humble/setup.bash" >> /home/${USERNAME}/.bashrc \
&&  echo "source /home/${USERNAME}/colcon_ws/install/setup.bash" >> /home/${USERNAME}/.bashrc \
# make everything we installed into the user's home directory 
# actually owned by the user...
&&  chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# finally switch to the user we created for normal use
USER ${USERNAME}

ENTRYPOINT ["/bin/bash"]



