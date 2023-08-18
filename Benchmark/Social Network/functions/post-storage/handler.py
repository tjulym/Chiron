import pymongo
import json
from time import time

mongo_url = "mongodb://post-storage-mongodb.socialnetwork-db.svc.cluster.local:27017/"

myclient = pymongo.MongoClient(mongo_url)
mydb = myclient['post']
mycol = mydb["post"]

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = json.loads(req)

    response = {"time": {"post-storage": {"start_time": start}}}

    post = {"text": event["body"]["text"],
        "urls": event["body"]["urls"],
        "creator": event["body"]["creator"],
        "media": event["body"]["medias"],
        "post_id": event["body"]["post_id"],
        "user_mentions": event["body"]["user_mentions"],
        "timestamp": time()}

    mycol.insert_one(post)

    response["time"].update(event["time"])

    response["time"]["post-storage"]["end_time"] = time()

    return json.dumps(response)

    return str(time() - start)
