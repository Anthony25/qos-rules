#!/usr/bin/python
# Author: Anthony Ruhier

# INTERFACES
INTERFACES = {
    "public_if": {  # network card which has the public IP
        "name": "eth1",
        "if_speed": 1048576,
        "speed": 20000,  # Upload
    },

    "lan_if": {  # network card for the LAN subnets
        "name": "eth0",
        "if_speed": 50000000,
        "speed": 30000,  # Download
    },

    "tun_online": {  # gre tunnel with online dedibox
        "name": "tun-srvo-02",
    },
}

# Because of torrents and overhead
INTERFACES["tun_online"]["speed"] = (
    INTERFACES["public_if"]["speed"] * 0.95 - 250
)

# If enabled, this script will not execute any command, just prints it
DEBUG = False
