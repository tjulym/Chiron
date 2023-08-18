import json
import time

def fibonacci(n):
    if n<=1:
        return n
    else:
        return fibonacci(n-1) + fibonacci(n-2)

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()
    thread_start = time.thread_time()

    event = {}
    response = {"time": {"fibonacci": {"start_time": start, "thread_start_time": thread_start}}}
    count = 23
    event = json.loads(req)

    fibonacci(count)

    response["body"] = event
    response["time"]["fibonacci"]["thread_end_time"] = time.thread_time()
    response["time"]["fibonacci"]["end_time"] = time.time()
    return json.dumps(response)
