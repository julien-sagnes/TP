## Dockerized PincherX

This repository provides dockerization to control the [PincherX-100 robot](https://www.trossenrobotics.com/pincherx-100-robot-arm.aspx) by [Trossen Robotics](https://www.trossenrobotics.com/).
The PincherX robots is suitable pedagogical tool for robotic course, and dockerizing the controllers has several advantages:
- easier and faster setup for teachers
- corss platform compatibility (Ubuntu or Windows)
- hiding all the mess from students
- code maintantence

## Installation

- For **Ubuntu**, make sure you have Docker installed. To do this, follow the the [official instruction](https://docs.docker.com/engine/install/ubuntu/). 
- For **Windows**, make sure you have WSL2, DockerDesktop, and usbipd installed; instructions here: [Windows](installation_windows.md)


### Clone the repository
Before cloning, you might need to disable git ``autocrlf`` by bashing first and:
```bash
git config --global core.autocrlf false
```
Otherwise, you might have some end-of-the-line issues with bash files.

Choose a local folder on your PC and clone this git repository:
```bash
git clone https://gitlab.isir.upmc.fr/khoramshahi/dockerized-pincherx.git
```
Go the repo folder:
```bash
cd dockerized-pincherx
```

### Run the script
The provided script will download a docker image, and runs in a container.

A few remarks:
- When running the first time, downloading and loading might take a few minutes.
- Downlaoding the pre-build image is much faster than performing a `docker build`
- You can copy-paste the tar file into a usb-key and paste on different PCs to be even faster and avoid dowloading a big file severa time.
- The script can be run both on Ubuntu and Windows (with WSL2 and DockerDesktop).
- The script tries to find the robot over USB and if not found, it still proivdes a simulation in Rviz.
- The script is quite verbose, so please attention for the output.

Make sure that the script is executable:
```bash
chmod +x run_pincher.sh
```

Run the script:
```bash
bash run_pincher.sh
```

If successful, you will get an interactive terminal in the container. 

### Test the installation

When the interactive terminal is ready, run the controller.

- If the robot is found:
``` bash
roslaunch interbotix_xsarm_control xsarm_control.launch robot_model:=px100
```

- If the robot is not found (only simulation in Rviz):
``` bash
roslaunch interbotix_xsarm_control xsarm_control.launch robot_model:=px100 use_sim:=true
```

In another terminal, get another docker interative terminal by:
```bash
docker exec -it px100 bash
```
Then go to the folder with python codes:
```bash
cd python_codes
```
and run the python code to move the robot:
```bash
python3 bartender.py
```
You should see the robot moving in real life (if found) and in Rviz (simulated if not found). 











