import json
import time

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    event = json.loads(req)

    response = {"time": {"upload-media": {"start_time": start}}}
    
    media_ids = (event["body"]["media_ids"]).split(",")
    media_types = (event["body"]["media_types"]).split(",")

    medias = []
    for m in zip(media_ids, media_types):
        media = {"id": m[0].strip(), "type": m[1].strip()}
        medias.append(media)

    response["body"] = {"medias": medias}
    response["time"].update(event["time"])

    response["time"]["upload-media"]["end_time"] = time.time()

    return json.dumps(response) 
