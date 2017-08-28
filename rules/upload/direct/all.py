from pyqos.algorithms.htb import HTBClass, HTBFilterFQCodel

from rules import app
from rules.qos_formulas import burst_formula, cburst_formula


UPLOAD = app.config["INTERFACES"]["public_if"]["speed"]
MIN_UPLOAD = 200


class OnlineTunnel(HTBFilterFQCodel):
    """
    Class for tunnel with Online

    As almost all traffic is going through the tunnel, very high priority.
    """
    parent = "1:1"
    classid = "1:100"
    prio = 20
    mark = 100
    rate = UPLOAD - MIN_UPLOAD
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15


class Default(HTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:500"
    prio = 50
    mark = 500
    rate = UPLOAD
    burst = burst_formula(rate)
    limit = burst
    interval = 15


class Torrents(HTBFilterFQCodel):
    """
    Class for torrents

    Very low priority.
    """
    classid = "1:600"
    prio = 100
    mark = 600
    rate = MIN_UPLOAD
    ceil = UPLOAD
    burst = burst_formula(rate)
    cburst = cburst_formula(rate, burst)
    limit = cburst
    interval = 15
