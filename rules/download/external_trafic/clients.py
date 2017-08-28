from pyqos.algorithms.htb import HTBClass, HTBFilterFQCodel

from rules import app
from rules.qos_formulas import burst_formula, cburst_formula


DOWNLOAD = app.config["INTERFACES"]["lan_if"]["speed"]
UPLOAD = app.config["INTERFACES"]["public_if"]["speed"]


class Interactive(HTBFilterFQCodel):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    classid = "1:110"
    prio = 10
    mark = 110
    rate = DOWNLOAD * 30/100
    ceil = DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)


class TCP_ack(HTBFilterFQCodel):
    """
    Class for TCP ACK.

    It's important to receive quickly the TCP ACK when uploading. Uses htb then
    fq-codel.
    """
    classid = "1:120"
    prio = 20
    mark = 120
    rate = UPLOAD / 10
    ceil = DOWNLOAD / 10
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class SSH(HTBFilterFQCodel):
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
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class HTTP(HTBFilterFQCodel):
    """
    Class for HTTP/HTTPS connections.
    """
    classid = "1:1200"
    prio = 40
    mark = 1200
    rate = DOWNLOAD * 10/100
    ceil = DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class Default(HTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:1500"
    prio = 100
    mark = 1500
    rate = DOWNLOAD * 20/100
    ceil = DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class Main(HTBClass):
    classid = "1:11"
    rate = DOWNLOAD * 70/100
    ceil = DOWNLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
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
