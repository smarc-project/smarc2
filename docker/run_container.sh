docker run --rm -it \
    --network=host \
    --ipc=host \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $PWD:/home/smarc2user/colcon_ws \
    -v $PWD/src/smarc2/docker/vscode:/home/smarc2user/colcon_ws/.vscode \
    smarc2/base