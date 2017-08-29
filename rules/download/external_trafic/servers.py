from rules import app
from rules.custom_qos_class import CustomHTBClass, CustomHTBFilterFQCodel


DOWNLOAD = app.config["INTERFACES"]["lan_if"]["speed"]
MIN_DOWNLOAD = DOWNLOAD/10
UPLOAD = app.config["INTERFACES"]["public_if"]["speed"]


class Interactive(CustomHTBFilterFQCodel):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    classid = "1:210"
    prio = 10
    mark = 210
    rate = DOWNLOAD * 10/100
    ceil = DOWNLOAD


class OpenVPN(CustomHTBFilterFQCodel):
    """
    Class for openvpn.

    We want openvpn to be fast
    """
    classid = "1:215"
    prio = 15
    mark = 215
    rate = UPLOAD  # It has to send almost the same data it receives
    ceil = UPLOAD * 2


class TCP_ack(CustomHTBFilterFQCodel):
    """
    Class for TCP ACK.

    It's important to let the ACKs leave the network as fast as possible when a
    host of the network is downloading
    """
    classid = "1:220"
    prio = 20
    mark = 220
    rate = UPLOAD / 10
    ceil = DOWNLOAD / 10


class IRC(CustomHTBFilterFQCodel):
    """
    Class for IRC or services that doesn't need a lot of bandwidth but have to
    be quick.

    A bit low priority
    """
    classid = "1:2100"
    prio = 30
    mark = 2100
    rate = 100
    ceil = DOWNLOAD/2


class Downloads(CustomHTBFilterFQCodel):
    """
    Class for torrents and direct downloads

    A bit high priority, I don't want to wait for my movie :p
    """
    classid = "1:2600"
    prio = 50
    mark = 2600
    rate = DOWNLOAD * 20/100
    ceil = DOWNLOAD


class Default(CustomHTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:2500"
    prio = 100
    mark = 2500
    rate = MIN_DOWNLOAD
    ceil = DOWNLOAD


class Main(CustomHTBClass):
    classid = "1:12"
    rate = MIN_DOWNLOAD
    ceil = DOWNLOAD
    prio = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_child(
            Interactive(),
            OpenVPN(),
            TCP_ack(),
            IRC(),
            Downloads(),
            Default(),
        )
