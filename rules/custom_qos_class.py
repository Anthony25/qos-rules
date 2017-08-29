from pyqos.algorithms.htb import HTBClass, HTBFilterFQCodel

from rules.qos_formulas import burst_formula, cburst_formula


class CustomHTBClass(HTBClass):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.burst = burst_formula(self.rate)
        self.cburst = cburst_formula(self.rate, self.burst)


class CustomHTBFilterFQCodel(HTBFilterFQCodel):
    """
    Class for torrents and direct downloads

    A bit high priority, I don't want to wait for my movie :p
    """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.burst = burst_formula(self.rate)
        self.cburst = cburst_formula(self.rate, self.burst)
        self.limit = self.cburst
        self.interval = 15
