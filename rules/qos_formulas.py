def burst_formula(obj, post_compute=None):
    """
    Cisco formula to calculates the burst

    :param post_compute: lambda to apply on the computed burst
    """
    burst = 0.2 * obj.rate / 8

    if post_compute:
        burst = post_compute(burst)

    # Avoid overflow.
    if burst > 2**22:
        return 2**22 - 1
    return burst


def cburst_formula(obj, post_compute=None):
    """
    Cisco formula to calculates the cburst

    :param post_compute: lambda to apply on the computed cburst
    """
    cburst = 0.5 * obj.rate / 8 + obj.burst

    if post_compute:
        cburst = post_compute(cburst)

    # Avoid overflow.
    if cburst > 2**22:
        return 2**22 - 1
    return cburst
