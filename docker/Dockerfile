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

# install rosdep dependencies and then delete the source
# you should volume mount your source code into the container during runtime instead!
COPY src /tmp/src
RUN apt-get update && rosdep update \
    && rosdep install -i --from-path /tmp/src --rosdistro humble -y --skip-keys sam_* --skip-keys lolo_* --skip-keys smarc_* \
    && rm -rf /tmp/src

# create a non-root user for most things, including ros2
ARG UID=1000
ARG GID=1000
ARG USERNAME=smarc2user
RUN adduser --quiet --disabled-password --gecos '' --uid ${UID:=1000} --uid ${GID:=1000} ${USERNAME} \
&& usermod -aG sudo ${USERNAME}

# Allow the user to use sudo without a password
RUN echo "${USERNAME} ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers

WORKDIR /home/${USERNAME}

# make everything we installed into the user's home directory 
# actually owned by the user...
RUN chown -R ${USERNAME}:${USERNAME} /home/${USERNAME}

# make colcon behave by adding this defaults file
COPY src/smarc2/docker/defaults.yaml .colcon/defaults.yaml

RUN mkdir colcon_ws
WORKDIR /home/${USERNAME}/colcon_ws

# Edit ~/.bashrc contents
COPY src/smarc2/docker/custom_bashrc.sh /tmp/custom_bashrc.sh
RUN cat /tmp/custom_bashrc.sh >> /home/${USERNAME}/.bashrc \
    && source /home/${USERNAME}/.bashrc \
    && rm /tmp/custom_bashrc.sh

# Install python requirements
COPY src/smarc2/docker/requirements.txt /tmp/requirements.txt
RUN pip install -r /tmp/requirements.txt \
    && rm /tmp/requirements.txt

COPY src/smarc2/docker/apt-requirements.txt /tmp/apt-requirements.txt
RUN if [ -s /tmp/apt-requirements.txt ]; then \
        apt-get update && xargs -a /tmp/apt-requirements.txt apt-get -y install; \
    else \
        echo "No Packages to install."; \
    fi \
    && rm /tmp/apt-requirements.txt \
    && rm -rf /var/lib/apt/lists/*

# finally switch to the user we created for normal use
USER ${USERNAME}

ENTRYPOINT ["/bin/bash"]



