#!/usr/bin/python
# Author: Anthony Ruhier

# INTERFACES
INTERFACES = {
    "public_if": {  # network card which has the public IP
        "name": "eth1",
        "if_speed": 960 * 2**10,
        "speed": 230 * 2**10,  # Upload
    },

    "lan_if": {  # network card for the LAN subnets
        "name": "eth0",
        "if_speed": 50 * 2**20,
        "speed": 920 * 2**10,  # Download
    },

    "tun_online": {  # gre tunnel with online dedibox
        "name": "tun-srvo-02",
    },
}

# Because of overhead
INTERFACES["tun_online"]["speed_lambda"] = lambda s: s * 0.95 - 250
INTERFACES["tun_online"]["speed"] = INTERFACES["tun_online"]["speed_lambda"](
    INTERFACES["public_if"]["speed"]
)

# If enabled, this script will not execute any command, just prints it
DEBUG = False
