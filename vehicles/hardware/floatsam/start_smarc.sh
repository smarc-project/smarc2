#!/bin/bash

# Define the container name
CONTAINER_NAME="smarc2"

# Go to the correct folder
cd ~/smarc2

# Check if the container already exists (stopped or running)
if [ "$(docker ps -aq -f name=${CONTAINER_NAME})" ]; then
    # Check if it is currently running
    if [ "$(docker ps -q -f name=${CONTAINER_NAME})" ]; then
        echo "Container is already running. Entering..."
        docker exec -it ${CONTAINER_NAME} bash
    else
        echo "Resuming stopped container..."
        docker start -ai ${CONTAINER_NAME}
    fi
else
    echo "Creating a NEW container..."    
    
    # Note: Added --network host to allow PX4 UDP packets to reach the container
    docker run -it \
        --device=/dev/gps_rtk_0:/dev/gps_rtk_0 \
        --device=/dev/gps_rtk_1:/dev/gps_rtk_1 \
        --name ${CONTAINER_NAME} \
        --network host \
        -v $(pwd):/home/smarc2user/colcon_ws/src/smarc2 \
        smarc2
fi  