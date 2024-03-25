#!/bin/bash
# notice the . at the end!
docker build -t smarc2/base --build-arg UID=$(id -u) --build-arg GID=$(id -g) --build-arg USERNAME=$(whoami)  -f docker/Dockerfile .
