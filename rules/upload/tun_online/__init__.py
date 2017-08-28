from pyqos.algorithms.htb import RootHTBClass

from rules import app
from .clients import Main as Clients
from .servers import Main as Servers


tun_online = app.config["INTERFACES"]["tun_online"]
tun_root_class = RootHTBClass(
    interface=tun_online["name"],
    rate=tun_online["speed"],
    burst=tun_online["speed"]/8,
    qdisc_prefix_id="1:",
    default=1500
)

tun_root_class.add_child(Clients(), Servers())
app.run_list.append(tun_root_class)
