In4Labs - Systems Integration remote lab
=====
# Description
Implementation of the Systems Integration remote lab inside a Docker container that will be run by [In4Labs base LTI tool](https://github.com/cRejon/in4labs).   
Tested on Raspberry Pi OS Lite Bullseye (64-bit).  
Requires Python >=3.9.

# Installation
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
## Arduino USB connections
Connect each Arduino board to the Raspberry Pi according to boards configuration.
```
# Boards configuration
boards = {
    'Board_1':{
        'name':'Sensor',
         ...
        'usb_port':'1',
    },
    'Board_2':{
        'name':'TFT',
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

# Testing
## Setup Raspberry Pi
### Docker installation
``` bash
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh
sudo apt-get install -y uidmap
dockerd-rootless-setuptool.sh install
rm get-docker.sh
```
### Python packages
``` bash
sudo apt install -y python3-docker
```
## Running
Execute the **_test.py_** file inside _test folder_ and go in your browser to the given url.  
The Docker container is created via the Dockerfile <ins>only</ins> the first time this script is run. This will take some time, so please be patient.  
On the login page, enter ```admin@email.com``` as user.


