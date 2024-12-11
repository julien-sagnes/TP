#!/bin/bash

IMAGE_NAME="ros_pincher"
IMAGE_TAR_NAME="ros_pincher_image.tar"
DOWNLOAD_URL="https://dropsu.sorbonne-universite.fr/s/Z5Yn3d6oqF6Amqz/download/ros_pincher_image.tar"

CHECKMARK="\u2713"
CROSSMARK="\u2718"

# ANSI color code for orange-like color (usually 33m or 38;5;214 for more terminals)
ORANGE='\033[38;5;214m'
RED='\033[31m'
RESET='\033[0m'

echo "> (run_pincher) - Looking for the docker image: $IMAGE_NAME ..."
if [[ -n "$(docker images -q "$IMAGE_NAME")" ]]; then
    echo -e "> (run_pincher) $CHECKMARK Docker image '$IMAGE_NAME' already exists."
    # Retrieve creation date and size of the image
    CREATED=$(docker image inspect --format='{{.Created}}' "$IMAGE_NAME" | cut -d'T' -f1)
    SIZE=$(docker image inspect --format='{{.Size}}' "$IMAGE_NAME")

    # Convert size from bytes to a human-readable format
    SIZE_HR=$(numfmt --to=iec --suffix=B "$SIZE")

    # Display the information on a single line
    echo -e "> (run_pincher) - Docker image '$IMAGE_NAME' - Created on: $CREATED, Size: $SIZE_HR"
else
    echo "> (run_pincher) - Docker image '$IMAGE_NAME' not found."
    echo "> (run_pincher) - Looking for the tar file: $IMAGE_TAR_NAME ..."

    # Check if the file exists
    if [ -f "$IMAGE_TAR_NAME" ]; then
        echo -e "> (run_pincher) $CHECKMARK $IMAGE_TAR_NAME already exists."
    else
        echo "> (run_pincher) - cannot find $IMAGE_TAR_NAME"
        echo "> (run_pincher) - Downloading from: $DOWNLOAD_URL"
        echo "> (run_pincher) - Running wget command..."
        wget -c "$DOWNLOAD_URL"

        # Verify the download was successful
        if [ -f "$IMAGE_TAR_NAME" ]; then
            echo -e "> (run_pincher) $CHECKMARK $IMAGE_TAR_NAME downloaded successfully."
        else
            echo -e "> (run_pincher) ${RED}$CROSSMARK Failed to download $IMAGE_TAR_NAME.${RESET}"
            exit 1
        fi
    fi

    echo "> (run_pincher) Loading the Docker image into Docker ..."
    docker load -i "$IMAGE_TAR_NAME"
    if [[ -n "$(docker images -q "$IMAGE_NAME")" ]]; then
        echo -e "> (run_pincher) $CHECKMARK Docker image '$IMAGE_NAME' loaded successfully."
    else
        echo -e "> (run_pincher) ${RED}$CROSSMARK Docker image '$IMAGE_NAME' failed to load.${RESET}"
        exit 1
    fi
fi



# Check for interbotix udev rules file
# the udev is necessary to find the robot as /dev/ttyDXL
if [ -e /etc/udev/rules.d/99-interbotix-udev.rules ]; then
    echo -e "> (run_pincher) $CHECKMARK interbotix udev file found"
else
    echo -e "> (run_pincher) Interbotix udev file NOT found. Downloading..."
    curl https://raw.githubusercontent.com/Interbotix/interbotix_ros_core/main/interbotix_ros_xseries/interbotix_xs_sdk/99-interbotix-udev.rules > 99-interbotix-udev.rules
    sudo cp 99-interbotix-udev.rules /etc/udev/rules.d/
    sudo udevadm control --reload-rules && sudo udevadm trigger
    sudo service udev restart
fi



# Base Docker run command
DOCKER_RUN_CMD="docker run -it --rm --privileged --net host --name px100"

# Check if running on WSL or native Ubuntu
if grep -qEi "(Microsoft|WSL)" /proc/version &> /dev/null; then

    # Running on WSL
    echo "> (run_pincher) - Detected WSL environment."

    # Check if robot is connected via USB
    if [ -e /dev/ttyDXL ]; then
        echo -e "> (run_pincher) $CHECKMARK The robot is found over the USB in WSL."
        ls -la /dev | grep ttyDXL

        DOCKER_RUN_CMD="$DOCKER_RUN_CMD --device=/dev/ttyDXL:/dev/ttyDXL"
    else 
        echo -e "> (run_pincher) ${ORANGE}! The robot is not connected via USB in WSL. Only simulation will work.${RESET}"
    fi

    # Check for WSLg (X11 support)
    if [ -d /mnt/wslg ]; then
        echo -e "> (run_pincher) $CHECKMARK The WSLg is available."
        DOCKER_RUN_CMD="$DOCKER_RUN_CMD -v /mnt/wslg:/mnt/wslg -v /mnt/wslg/.X11-unix:/tmp/.X11-unix"
    else 
        echo -e "> (run_pincher) ${RED}$CROSSMARK The WSLg folder is not found on default WSL 2. Rviz will not work.${RESET}"
        exit 1
    fi


else
    # Running on native Ubuntu
    echo " (run_pincher) - Detected native Ubuntu environment."


    # Check if robot is connected via USB
    if [ -e /dev/ttyDXL ]; then
        echo -e "> (run_pincher) $CHECKMARK The robot is found over the USB."
        ls -la /dev | grep ttyDXL

        DOCKER_RUN_CMD="$DOCKER_RUN_CMD -v /dev/ttyDXL:/dev/ttyDXL"
    else 
        echo -e "> (run_pincher) ${ORANGE}$CROSSMARK The robot is not connected via USB in WSL. Only simulation will work.${RESET}"
    fi

    # Check if X11 is available
    if [ -d /tmp/.X11-unix ]; then
        echo -e "> (run_pincher) $CHECKMARK The X11-unix is available."
        xhost +local:docker
        xhost +si:localuser:root

        DOCKER_RUN_CMD="$DOCKER_RUN_CMD -v /tmp/.X11-unix:/tmp/.X11-unix"
    else 
        echo -e "> (run_pincher) $CROSSMARK The X11-unix folder is not found. Rviz will not work!"
        exit 1
    fi
fi

DOCKER_RUN_CMD="$DOCKER_RUN_CMD -v \"$(pwd)/python_codes:/python_codes\" ros_pincher"


# Run the Docker container
# for debugging purposes
# echo "> (run_pincher) command: $DOCKER_RUN_CMD"

echo "> (run_pincher) - Running the docker image ..."
eval $DOCKER_RUN_CMD
