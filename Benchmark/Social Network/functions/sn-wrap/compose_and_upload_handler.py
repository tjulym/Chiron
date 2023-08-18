import json
import time

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    events = json.loads(req)
    events = [json.loads(event) for event in events]

    body = {}
    response = {"time": {"compose-and-upload": {"start_time": start}}}
    
    if len(events) < 5:
        body = 'Incomplete arguments'
    else:
        try:
            for event in events:
                body.update(event["body"])
                response["time"].update(event["time"])
        except Exception as e:
            body = 'Incomplete arguments'
    
    response["body"] = body
    response["time"]["compose-and-upload"]["end_time"] = time.time()
    return json.dumps(response)
