from pyqos.algorithms.htb import HTBClass

from rules import app
from rules.qos_formulas import burst_formula
from .clients import Main as Clients
from .servers import Main as Servers


DOWNLOAD = app.config["INTERFACES"]["lan_if"]["if_speed"]


class Main(HTBClass):
    classid = "1:10"
    prio = 0
    rate = DOWNLOAD
    ceil = DOWNLOAD
    burst = burst_formula(rate) * 3
    qdisc_prefix_id = "1:"
    default = 10

    def __init__(self, *args, **kwargs):
        r = super().__init__(*args, **kwargs)
        self.add_child(Clients(), Servers())
