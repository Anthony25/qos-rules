from rules import app
from rules.custom_qos_class import CustomHTBClass
from .clients import Main as Clients



class Main(CustomHTBClass):
    classid = "1:10"
    prio = 0
    rate = (100, )
    qdisc_prefix_id = "1:"
    mark = 0x1000
    default = 0x1000

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # self.add_child(Clients(), Servers())

        clients = Clients()
        self.add_child(clients)
        # public if
        clients.declare_children_for_prefix(0x1100)
        # tunnel
        # clients.declare_children_for_prefix(
        #     0x1200, app.config["INTERFACES"]["tun_online"]["speed_lambda"]
        # )
