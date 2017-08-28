from pyqos.algorithms.htb import HTBFilterFQCodel

from rules import app
from rules.qos_formulas import burst_formula


LAN_IF_SPEED = app.config["INTERFACES"]["lan_if"]["if_speed"]


class InterVlan(HTBFilterFQCodel):
    """
    Intervlan need to be fast
    """
    classid = "1:15"
    rate = LAN_IF_SPEED
    burst = burst_formula(rate) * 3
    limit = burst
    interval = 10
    codel_quantum = 1514
    prio = 0
    mark = 10
