from pyqos.algorithms.htb import RootHTBClass

from rules import app
from rules.qos_formulas import burst_formula
from .all import Main


public_if = app.config["INTERFACES"]["public_if"]
public_if_root_class = RootHTBClass(
    interface=public_if["name"],
    rate=public_if["speed"],
    burst=(burst_formula, ),
    qdisc_prefix_id="1:",
    default=0xa
)

public_if_clients = Main()
public_if_root_class.add_child(public_if_clients)
public_if_clients.declare_children_for_prefix(0x1100)

app.run_list.append(public_if_root_class)


tun_if = app.config["INTERFACES"]["tun_online"]
tun_if_root_class = RootHTBClass(
    interface=tun_if["name"],
    rate=tun_if["speed"],
    burst=(burst_formula, ),
    qdisc_prefix_id="1:",
    default=0xa
)

tun_if_clients = Main()
tun_if_root_class.add_child(tun_if_clients)
tun_if_clients.declare_children_for_prefix(0x1200)

app.run_list.append(tun_if_root_class)
