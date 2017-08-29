from rules import app
from rules.custom_qos_class import CustomHTBClass
from .clients import Main as Clients
from .servers import Main as Servers


DOWNLOAD = app.config["INTERFACES"]["lan_if"]["if_speed"]


class Main(CustomHTBClass):
    classid = "1:10"
    prio = 0
    rate = DOWNLOAD
    ceil = DOWNLOAD
    qdisc_prefix_id = "1:"
    default = 10

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_child(Clients(), Servers())
