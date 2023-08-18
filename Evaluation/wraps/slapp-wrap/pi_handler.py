import json
import time
from decimal import Decimal, getcontext

def pi(digits):
    getcontext().prec = digits
    getcontext().prec += 2
    three = Decimal(3)
    lasts, t, s, n, na, d, da = 0, three, 3, 1, 0, 0, 24
    while s != lasts:
        lasts = s
        n, na = n+na, na+8
        d, da = d+da, da+32
        t = (t * n) / d
        s += t
    getcontext().prec -= 2
    return +s

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()
    thread_start = time.thread_time()

    event = {}
    response = {"time": {"pi": {"start_time": start, "thread_start_time": thread_start}}}
    count = 1000
    event = json.loads(req)

    pi(count)

    response["body"] = event
    response["time"]["pi"]["thread_end_time"] = time.thread_time()
    response["time"]["pi"]["end_time"] = time.time()
    return json.dumps(response)
