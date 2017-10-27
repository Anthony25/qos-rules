from rules import app
from rules.custom_qos_class import CustomHTBClass, CustomHTBFilterFQCodel


DOWNLOAD = app.config["INTERFACES"]["lan_if"]["speed"]
UPLOAD = app.config["INTERFACES"]["public_if"]["speed"]


class TCP_ack(CustomHTBFilterFQCodel):
    """
    Class for TCP ACK.

    It's important to receive quickly the TCP ACK when uploading. Uses htb then
    fq-codel.
    """
    classid = "1:120"
    prio = 10
    mark = 120
    rate = UPLOAD / 10
    ceil = DOWNLOAD / 10


class Interactive(CustomHTBFilterFQCodel):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    classid = "1:110"
    prio = 20
    mark = 110
    rate = DOWNLOAD * 30/100
    ceil = DOWNLOAD


class SSH(CustomHTBFilterFQCodel):
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !  fq-codel will mix the packets
    if there are several SSH connections in parallel and ensure that none has
    the priority
    """
    classid = "1:1100"
    prio = 30
    mark = 1100
    rate = 400
    ceil = DOWNLOAD


class HTTP(CustomHTBFilterFQCodel):
    """
    Class for HTTP/HTTPS connections.
    """
    classid = "1:1200"
    prio = 40
    mark = 1200
    rate = DOWNLOAD * 10/100
    ceil = DOWNLOAD


class Default(CustomHTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:1500"
    prio = 100
    mark = 1500
    rate = DOWNLOAD * 20/100
    ceil = DOWNLOAD


class Main(CustomHTBClass):
    classid = "1:11"
    rate = DOWNLOAD * 70/100
    ceil = DOWNLOAD
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
