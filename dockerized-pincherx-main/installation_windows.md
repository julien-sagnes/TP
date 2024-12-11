## WSL 2 on Windows 10/11
We will be running docker images inside Windows WSL 2. This approach provides simpler solution for passing USB devices and graphical interfaces later!

First, in a Windows terminal try:
```powershell
bash
```
If you do not have WSL, you will get

`
Windows Subsytem for Linux has no intalled distribution. So, skip to the next step.

`
If you a get the Linux promt, you can check the version by:
```shell
uname -a
```
and you need to see Linux followed by ``-microsoft-standard-WSL2``.

### Installing WSL 2 on Windows 10/11

The official WSL installation can be found [here](https://learn.microsoft.com/en-us/windows/wsl/install), but essentially you need to open Windows terminal and execute:
```powershell
wsl --install
```
** On windows 10, you might need to enable ``Windows Subsystem for Linux`` in Windows Features.

Create your user account in Linux/Ubuntu, and check for the version of the linux:
```shell
lsb_release -a
```
If you need to install another Ubuntu version, you can install it from Microsoft app store. 

update your ubuntu:
```shell
sudo apt update && sudo apt full-upgrade
```

### using WSL version 2
Now, on a windows terminal check the version of WSL
```powershell
wsl -l -v
```
Verify that your desired destribution has a star on the left side (meaning it is the default distribution) and it has version 2.
To update the version from 1 to 2:
```shell
wsl --set-version <distro-name> 2
```

To set the default distribution:
```shell
wsl --set-default-version <distro-name>
```

## Installing DockerDesktop
Install Docker desktop from [here](https://www.docker.com/products/docker-desktop/).
Run Docker Desktop and make sure that 
- "Use the WSL 2 based engine" is enable in the settings
- In the lower-left corner you see "Engine running"

To check if the docker can be run from WSL, run this command in WSL ('bash' if you're in a windows terminal)
```shell
 docker -v
 ```
You should get a similar message as:
`
Docker version 24.0.6, build ed223bc
`


## Passing USB device to WSL 2
Official instruction to connect Usb devices to WSL can be found [here](https://learn.microsoft.com/en-us/windows/wsl/connect-usb). However, here is the short and adapted version for pincher.

Connect the robot via usb cable to your pc.
On the Ubuntu terminal, you can check the list of usb devices:
```shell
lsusb
``` 
of course you don't see the robot! but it is useful to see the default list of usb connections for your WSL.

To see pass the USB we need to install usbipd both on the native windows machine and WSL Ubuntu.

On the Ubuntu terminal, install usbip on the Ubunut:
```shell
sudo apt install linux-tools-generic hwdata
```
then:
```shell
sudo update-alternatives --install /usr/local/bin/usbip usbip /usr/lib/linux-tools/*-generic/usbip 20
```
You need to get:<br>``update-alternatives: using /usr/lib/linux-tools/5.15.0-82-generic/usbip to provide /usr/local/bin/usbip (usbip) in auto mode``


On the Windows terminal, install usbipd using the following command:
```powershell
winget install usbipd
```
The official instructions are [here](https://github.com/dorssel/usbipd-win).
**Some of these commands might be outdated! Please go to github page for the most updated way to use usbipd**

In a Windows terminal list the available usb devices:
```powershell
usbipd wsl list
```
The robot should appear similar to: 

``1-10   0403:6014  USB Serial Converter   Not attached``

The BUSID (1-10 in this case) varies for different robots, PCs, and USB prots.

we can connect the USB device to WSL using the following command.
```powershell
usbipd wsl attach -b 1-10
```
We get a message like:
<br>``usbipd: info: Using default WSL distribution 'Ubuntu-22.04'; specify the '--distribution' option to select a different one.``


Now, in the Ubuntu, we can verify if the usb device is correctly connected:
```shell
lsusb
```
You need to see something similar:
<br>``Bus 001 Device 004: ID 0403:6014 Future Technology Devices International, Ltd FT232H Single HS USB-UART/FIFO IC``
