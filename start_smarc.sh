#!/bin/bash

# Define the container name
CONTAINER_NAME="smarc2_docker"

# Go to the correct folder
cd ~/Desktop/smarc_docker/smarc2

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
    # Note: No --rm flag, so it saves when you exit
    docker run -it \
        --name ${CONTAINER_NAME} \
        -p 10000:10000 \
        -v $(pwd):/home/smarc2user/colcon_ws/src/smarc2 \
        smarc2
fi
