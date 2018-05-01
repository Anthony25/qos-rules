from rules import app
from rules.custom_qos_class import CustomHTBClass, CustomHTBFilterFQCodel


class TCP_ack(CustomHTBFilterFQCodel):
    """
    Class for TCP ACK.

    It's important to receive quickly the TCP ACK when uploading. Uses htb then
    fq-codel.
    """
    mark = 0x1
    rate = (10, )
    ceil = (100, )


class Interactive(CustomHTBFilterFQCodel):
    """
    Interactive Class, for low latency, high priority packets such as VOIP and
    DNS.

    Low priority, pass before everything else. Uses htb then pfifo.
    """
    mark = 0x2
    rate = (30, )
    ceil = (100, )


class VPN(CustomHTBFilterFQCodel):
    mark = 0x5
    rate = (50, )
    ceil = (100, )


class SSH(CustomHTBFilterFQCodel):
    """
    Class for SSH connections.

    We want the ssh connections to be smooth !  fq-codel will mix the packets
    if there are several SSH connections in parallel and ensure that none has
    the priority
    """
    mark = 0x10
    rate = (5, 400)
    ceil = (100, )


class HTTP(CustomHTBFilterFQCodel):
    """
    Class for HTTP/HTTPS connections.
    """
    mark = 0x20
    rate = (30, )
    ceil = (100, )


class Default(CustomHTBFilterFQCodel):
    """
    Default class
    """
    mark = 0
    rate = (20, )
    ceil = (100, )
    prio = 1000


class Main(CustomHTBClass):
    classid = "1:11"
    rate = (100, )
    prio = 0
    mark = 0x1000

    def declare_children_for_prefix(self, mark_prefix, speed_lambda=None):
        # :param speed_lambda: lambda to compute the new rate or ceil
        for c in (TCP_ack, Interactive, VPN, SSH, HTTP, Default):
            new_mark = c.mark + mark_prefix
            child = c(
                prio=(c.prio or c.mark), mark=new_mark, id=new_mark
            )
            self.add_child(child)

            # if speed_lambda:
            #     child.rate = speed_lambda(child.rate)
            #     if child.ceil:
            #         child.ceil = speed_lambda(child.ceil)
