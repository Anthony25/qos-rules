from pyqos.algorithms.htb import RootHTBClass

from rules import app
from rules.qos_formulas import burst_formula
from .intervlan import InterVlan as InterVlan
from .external_traffic import Main as ExternalTraffic


lan_if = app.config["INTERFACES"]["lan_if"]
root_class = RootHTBClass(
    interface=lan_if["name"],
    rate=lan_if["if_speed"],
    burst=(burst_formula, ),
    qdisc_prefix_id="1:",
    default=0xa,
)

root_class.add_child(InterVlan(), ExternalTraffic())
app.run_list.append(root_class)
