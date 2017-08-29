from rules import app
from rules.custom_qos_class import CustomHTBClass, CustomHTBFilterFQCodel


TUN_UPLOAD = app.config["INTERFACES"]["tun_online"]["speed"]


class Interactive(CustomHTBFilterFQCodel):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else.
    """
    classid = "1:110"
    prio = 10
    mark = 110
    rate = TUN_UPLOAD * 10/100
    ceil = TUN_UPLOAD * 90/100


class TCP_ack(CustomHTBFilterFQCodel):
    """
    Class for TCP ACK.

    It's important to let the ACKs leave the network as fast as possible when a
    host of the network is downloading.
    """
    classid = "1:120"
    prio = 20
    mark = 120
    rate = TUN_UPLOAD / 4
    ceil = TUN_UPLOAD


class SSH(CustomHTBFilterFQCodel):
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !
    fq-codel will mix the packets if there are several SSH connections in
    parallel and ensure that none has the priority
    """
    classid = "1:1100"
    prio = 30
    mark = 1100
    rate = TUN_UPLOAD * 10/100
    ceil = TUN_UPLOAD


class HTTP(CustomHTBFilterFQCodel):
    """
    Class for HTTP/HTTPS connections.
    """
    classid = "1:1200"
    prio = 40
    mark = 1200
    rate = TUN_UPLOAD * 20/100
    ceil = TUN_UPLOAD


class Default(CustomHTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:1500"
    prio = 100
    mark = 1500
    rate = TUN_UPLOAD/2
    ceil = TUN_UPLOAD


class Main(CustomHTBClass):
    classid = "1:11"
    rate = TUN_UPLOAD/2
    ceil = TUN_UPLOAD
    prio = 0

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_child(
            Interactive(),
            TCP_ack(),
            SSH(),
            HTTP(),
            Default(),
        )
