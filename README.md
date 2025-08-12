In4Labs - Systems Integration remote lab [![CC BY-NC-SA 4.0][cc-by-nc-sa-shield]][cc-by-nc-sa]
=====
# Description
Implementation of the Systems Integration lab inside a Docker image that will be run by the tools [In4Labs base LTI tool](https://github.com/cRejon/in4labs) (if using a LMS such as Moodle) or [In4Labs base auth tool](https://github.com/cRejon/in4labs_auth) (if basic authentication is desired).  
Tested on Raspberry Pi OS Lite Bullseye (64-bit). Requires Python >=3.9.

# Installation
## Arduino USB connections
This lab uses three [Arduino Nano ESP32](https://docs.arduino.cc/hardware/nano-esp32) boards to perform the experiments. Connect each board to the Raspberry Pi according to its **_'usb_port'_** variable inside the app _config.py_ file. These variables can be changed if more laboratories are installed on the same Raspberry Pi.
```
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
Go to _Localisation Options_ -> _WLAN Country_ and select your country.  

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
1. Install Docker through its bash script selecting the version to **25.0.5**:
```
sudo apt update
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh --version 25.0.5
```
2. Manage Docker as a non-root user:
``` 
sudo groupadd docker
sudo usermod -aG docker $USER
newgrp docker
```
### Python packages
```
sudo apt install -y python3-docker python3-bcrypt
```
## Running
Execute the **_test.py_** file inside _test folder_ and go in your browser to the given url.  
The Docker container is created via the Dockerfile <ins>only</ins> the first time this script is run. This will take some time, so please be patient.  
On the login page, enter ```admin@email.com``` as user.
# License
This work is licensed under a
[Creative Commons Attribution-NonCommercial-ShareAlike 4.0 International License][cc-by-nc-sa].

[![CC BY-NC-SA 4.0][cc-by-nc-sa-image]][cc-by-nc-sa]

[cc-by-nc-sa]: http://creativecommons.org/licenses/by-nc-sa/4.0/
[cc-by-nc-sa-image]: https://licensebuttons.net/l/by-nc-sa/4.0/88x31.png
[cc-by-nc-sa-shield]: https://img.shields.io/badge/License-CC%20BY--NC--SA%204.0-lightgrey.svg
