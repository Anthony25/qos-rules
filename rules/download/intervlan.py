from pyqos.algorithms.htb import HTBFilterPFIFO

from rules import app
from rules.qos_formulas import burst_formula


class InterVlan(HTBFilterPFIFO):
    """
    Intervlan need to be fast
    """
    classid = "1:15"
    rate = (100, )
    burst = (burst_formula, [], {"post_compute": lambda x: x*3})
    prio = 0
    mark = 0xa
