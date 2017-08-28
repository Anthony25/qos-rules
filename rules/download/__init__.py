from pyqos.algorithms.htb import RootHTBClass

from rules import app
from rules.qos_formulas import burst_formula
from .intervlan import InterVlan as InterVlan
from .external_trafic import Main as ExternalTrafic


lan_if = app.config["INTERFACES"]["lan_if"]
root_class = RootHTBClass(
    interface=lan_if["name"],
    rate=lan_if["if_speed"],
    ceil=lan_if["if_speed"],
    burst=burst_formula(lan_if["if_speed"]),
    qdisc_prefix_id="1:",
    default=10,
)

root_class.add_child(InterVlan(), ExternalTrafic())

app.run_list.append(root_class)
