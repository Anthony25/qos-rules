from rules import app
from rules.custom_qos_class import CustomHTBFilterFQCodel


UPLOAD = app.config["INTERFACES"]["public_if"]["speed"]
MIN_UPLOAD = 200


class OnlineTunnel(CustomHTBFilterFQCodel):
    """
    Class for tunnel with Online

    As almost all traffic is going through the tunnel, very high priority.
    """
    parent = "1:1"
    classid = "1:100"
    prio = 20
    mark = 100
    rate = UPLOAD - MIN_UPLOAD
    ceil = UPLOAD


class Default(CustomHTBFilterFQCodel):
    """
    Default class
    """
    classid = "1:500"
    prio = 50
    mark = 500
    rate = UPLOAD


class Torrents(CustomHTBFilterFQCodel):
    """
    Class for torrents

    Very low priority.
    """
    classid = "1:600"
    prio = 100
    mark = 600
    rate = MIN_UPLOAD
    ceil = UPLOAD
