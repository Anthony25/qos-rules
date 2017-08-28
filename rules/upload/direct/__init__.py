from pyqos.algorithms.htb import RootHTBClass

from rules import app
from .all import OnlineTunnel, Default, Torrents


public_if = app.config["INTERFACES"]["public_if"]
public_if_root_class = RootHTBClass(
    interface=public_if["name"],
    rate=public_if["speed"],
    burst=public_if["speed"]/8,
    qdisc_prefix_id="1:",
    default=500
)

public_if_root_class.add_child(OnlineTunnel(), Default(), Torrents())
app.run_list.append(public_if_root_class)
