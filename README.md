In4Labs - Systems Integration remote lab
=====
# Description
Implementation of the Systems Integration remote lab inside a Docker container that will be run by [In4Labs base LTI tool](https://github.com/cRejon/in4labs).   
Tested on Raspberry Pi OS Lite Bullseye (64-bit).  
Docker version 25.0.5 
Requires Python >=3.9 

# Installation
## Arduino USB connections
Connect each Arduino board to the Raspberry Pi according to boards configuration.
``` python
# Boards configuration
boards = {
    'Board_1':{
        'name':'Sensor',
         ...
        'usb_port':'1',
    },
    'Board_2':{
        'name':'LCD',
         ...
        'usb_port':'2',
    },
    'Board_3':{
        'name':'Fan',
         ...
        'usb_port':'3',
    }
}
```
If you look at the USB hub from the front, the port numbering is as follows.

                _______    _______ 
               | _____ |  | _____ | 
        3-->   ||_____||  ||_____||  <-- 1
               | _____ |  | _____ | 
        4-->   ||_____||  ||_____||  <-- 2
               |_______|__|_______|

## Create a wireless access point
1. Set WiFi country code
``` bash
sudo raspi-config
``` 
Go to _System Options_ -> _Wireless LAN_ and select your country.  

2. Install required packages
``` bash
sudo apt update
sudo apt install hostapd dnsmasq
sudo systemctl stop dnsmasq
sudo systemctl stop hostapd
```
3. Configure the access point host software
``` bash
sudo nano /etc/hostapd/hostapd.conf
```
Add the following content to this file, adjusting the *country_code* in which the lab is installed:
``` makefile
country_code=ES
interface=wlan0
driver=nl80211
ssid=In4Labs-WiFi
hw_mode=g
channel=7
ieee80211n=1
wmm_enabled=1
macaddr_acl=0
auth_algs=1
ignore_broadcast_ssid=0
wpa=2
wpa_key_mgmt=WPA-PSK
wpa_passphrase=password
rsn_pairwise=CCMP

```
4. Configure the DHCP server
``` bash
sudo mv /etc/dnsmasq.conf /etc/dnsmasq.conf.orig
sudo nano /etc/dnsmasq.conf
```
Add the following content:
``` go
interface=wlan0
dhcp-range=192.168.4.2,192.168.4.20,255.255.255.0,24h
```
5. Configure a static IP
``` bash
sudo nano /etc/dhcpcd.conf
``` 
Add the following lines at the end of the file:
``` java
interface wlan0
    static ip_address=192.168.4.1/24
    nohook wpa_supplicant
```
6. Start and Enable Services
``` bash
sudo systemctl unmask hostapd
sudo systemctl start hostapd
sudo systemctl start dnsmasq

sudo systemctl enable hostapd
sudo systemctl enable dnsmasq
```

# Testing
## Setup Raspberry Pi
### Docker installation
1. Run the following command to uninstall all conflicting packages:
``` bash
for pkg in docker.io docker-doc docker-compose podman-docker containerd runc; do sudo apt-get remove $pkg; done
```
2. Add Docker's official GPG key:
``` bash
sudo apt update
sudo apt-get install ca-certificates curl uidmap
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/debian/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
```
3. Add the repository to Apt sources:
``` bash
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] https://download.docker.com/linux/debian \
  $(. /etc/os-release && echo "$VERSION_CODENAME") stable" | \
  sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
```
4. Select the version 25.0.5 for Bullseye and install Docker:
``` bash
VERSION_STRING=5:25.0.5-1~debian.11~bullseye
sudo apt-get install docker-ce=$VERSION_STRING docker-ce-cli=$VERSION_STRING containerd.io
```
#### Set Rootless mode
1. Disable the system-wide Docker daemon:
``` bash
sudo systemctl disable --now docker.service docker.socket
sudo rm /var/run/docker.sock
```
2. Run dockerd-rootless-setuptool.sh install as a non-root user to set up the daemon:
``` bash
dockerd-rootless-setuptool.sh install
```
3. To run docker.service on system startup:
``` bash
sudo loginctl enable-linger pi
```
#### Change the permissions of the folder _/dev/bus/usb_ to be accessible by the current user (_pi_)
1. Create a new _udev_ rule file:
``` bash
sudo nano /etc/udev/rules.d/99-usb.rules
```
2. Add the following content to the file:
``` bash
SUBSYSTEM=="usb", GROUP="pi", MODE="0775"
```
3. Reload and trigger the new _udev_ rules:
``` bash
sudo udevadm control --reload-rules
sudo udevadm trigger
```

### Python packages
``` bash
sudo apt install -y python3-docker
```
## Running
Execute the **_test.py_** file inside _test folder_ and go in your browser to the given url.  
The Lab Docker container is created via the Dockerfile <ins>only</ins> the first time this script is run. This will take some time, so please be patient.  
On the login page, enter ```admin@email.com``` as user.


