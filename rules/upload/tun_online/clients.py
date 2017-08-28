from pyqos.algorithms.htb import HTBClass, HTBFilterFQCodel

from rules import app
from rules.qos_formulas import burst_formula, cburst_formula


TUN_UPLOAD = app.config["INTERFACES"]["tun_online"]["speed"]


class Interactive(HTBFilterFQCodel):
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
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)


class TCP_ack(HTBFilterFQCodel):
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
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class SSH(HTBFilterFQCodel):
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
    rate = TUN_UPLOAD * 20/100
    ceil = TUN_UPLOAD
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
    rate = TUN_UPLOAD/2
    ceil = TUN_UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class Main(HTBClass):
    classid = "1:11"
    rate = TUN_UPLOAD/2
    ceil = TUN_UPLOAD
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
