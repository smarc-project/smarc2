# Problem
The wireguard kernel module in not included by default on jetson AGX orin, so instead compiling it youself you can also use a non-kernel version of wireguard. This file contains instructions of how to do that. The guide might contain some unnecesary steps since once we have gotten this to work on the jetson we have not unistalled and verified several times.

## Step 1: Remove old versions of wireguard if they exist.


```bash
sudo apt-get purge -y wireguard-dkms
```

## Step 2: Install wireguard-go and wireguard-tools
```bash
sudo apt install wireguard-tools wireguard-go
```

## Reboot jetson
```bash
sudo reboot
```

## Step 3: Copy wireguard config file and enable wireguard service
```bash
sudo sudo cp wireguard_file.conf /etc/wireguard/
```

**wireguard_file** is the name of the config file without the ".conf"

```bash
sudo systemctl enable wg-quick@<wireguard_file>.service 
sudo systemctl daemon-reload
```

## Step 4: Check this file
```bash
sudo cat /usr/lib/systemd/system/wg-quick@.service
```
It should exist and contain something. If it does not run try restating the computer. If it still has no content try running 
```bash
sudo systemctl start wg-quick@<wireguard_file>.service
```

## Step 5: Add env variable to the service to tell it to use the userspace version of wireguard and reaload daemon
```bash
sudo vim /usr/lib/systemd/system/wg-quick@.service
sudo systemctl daemon-reload
```

Add this line after the other already existing "Environment" key:
```Bash
Environment=export WG_QUICK_USERSPACE_IMPLEMENTATION=wireguard
```

## Step 6: restart service / reboot computer
```bash
sudo systemctl restart wg-quick@<wireguard_file>
```