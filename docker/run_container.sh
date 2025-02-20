docker run -it \
    --network=host \
    --ipc=host \
    --env="DISPLAY" \
    --env="QT_X11_NO_MITSHM=1" \
    -v /tmp/.X11-unix:/tmp/.X11-unix:rw \
    -v $HOME/.vscode-server:/root/.vscode-server \
    -v $HOME/.vscode-server/extensions:/root/.vscode-server/extensions \
    -v $HOME/.vscode-server-insiders/extensions:/root/.vscode-server-insiders/extensions \
    -v $PWD:/home/smarc2user/colcon_ws \
    -v $PWD/src/smarc2/docker/vscode:/home/smarc2user/colcon_ws/.vscode \
    smarc2/base