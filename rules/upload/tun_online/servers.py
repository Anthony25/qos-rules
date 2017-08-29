from rules import app
from rules.custom_qos_class import CustomHTBClass, CustomHTBFilterFQCodel


TUN_UPLOAD = app.config["INTERFACES"]["tun_online"]["speed"]
MIN_UPLOAD = TUN_UPLOAD/10


class Interactive(CustomHTBFilterFQCodel):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else.
    """
    classid = "1:210"
    prio = 10
    mark = 210
    rate = TUN_UPLOAD * 10/100
    ceil = TUN_UPLOAD * 90/100


class OpenVPN(CustomHTBFilterFQCodel):
    """
    Class for openvpn.

    We want openvpn to be fast.
    """
    classid = "1:215"
    prio = 15
    mark = 215
    rate = TUN_UPLOAD/3
    ceil = TUN_UPLOAD


class TCP_ack(CustomHTBFilterFQCodel):
    """
    Class for TCP ACK.

    It's important to let the ACKs leave the network as fast as possible when a
    host of the network is downloading.
    """
    classid = "1:220"
    prio = 20
    mark = 220
    rate = MIN_UPLOAD
    ceil = TUN_UPLOAD


class IRC(CustomHTBFilterFQCodel):
    """
    Class for IRC or services that doesn't need a lot of bandwidth but have to
    be quick.

    A bit lower priority.
    """
    classid = "1:2100"
    prio = 30
    mark = 2100
    rate = 100
    ceil = TUN_UPLOAD/5


class Default(CustomHTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:2500"
    prio = 100
    mark = 2500
    rate = MIN_UPLOAD
    ceil = TUN_UPLOAD


class Torrents(CustomHTBFilterFQCodel):
    """
    Class for torrents

    Very low priority.
    """
    classid = "1:2600"
    prio = 150
    mark = 2600
    rate = MIN_UPLOAD
    ceil = TUN_UPLOAD


class Main(CustomHTBClass):
    classid = "1:12"
    rate = MIN_UPLOAD
    ceil = TUN_UPLOAD
    prio = 1

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_child(
            Interactive(),
            OpenVPN(),
            TCP_ack(),
            IRC(),
            Default(),
            Torrents(),
        )
