import json
import time

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    event = json.loads(req)

    response = {"time": {"compose-post": {"start_time": start}}}   
 
    try:
        media_ids = (event["media_ids"]).split(",")
        media_types = (event["media_types"]).split(",")
        if not (len(media_ids) == len(media_types)):
            return "Unmatched medias"
        
        user_id = event["user_id"]
        username = event["username"]
        text = event["text"]
        post_type = event["post_type"]

        response["body"] = event
    except Exception as e:
        response["body"] = "Incomplete arguments"

    response["time"]["compose-post"]["end_time"] = time.time()
    return json.dumps(response)
