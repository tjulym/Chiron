import json
import time

arguments = ["title", "text", "username", "password", "rating"]

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    event = json.loads(req)

    response = {"time": {"compose-review": {"start_time": start}}}

    complete = False
    try:
        for arg in arguments:
            if event[arg] == '':
                break
        complete = True
    except Exception as e:
                pass

    if complete:
        response["body"] = event
    else:
        response["body"] = "Incomplete arguments"

    response["time"]["compose-review"]["end_time"] = time.time()
    return json.dumps(response)
