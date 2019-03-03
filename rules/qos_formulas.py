def burst_formula(obj, post_compute=None):
    """
    Cisco formula to calculates the burst

    :param post_compute: lambda to apply on the computed burst
    """
    burst = 0.5 * obj.rate/8

    if post_compute:
        return post_compute(burst)
    return burst


def cburst_formula(obj, post_compute=None):
    """
    Cisco formula to calculates the cburst

    :param post_compute: lambda to apply on the computed cburst
    """
    cburst = 1.5 * obj.rate/8 + obj.burst

    if post_compute:
        return post_compute(cburst)
    return cburst
