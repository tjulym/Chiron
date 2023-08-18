from time import time
import pymongo
import json

"""
myclient = pymongo.MongoClient("mongodb://review-storage-mongodb.movie-reviewing.svc.cluster.local:27017/", connect=False)
mydb = myclient["review"]
mycol = mydb["review"]
"""
arguments = set(["review_id", "timestamp", "user_id", "movie_id", "text", "rating"])

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    myclient = pymongo.MongoClient("mongodb://review-storage-mongodb.movie-reviewing.svc.cluster.local:27017/")
    mydb = myclient["review"]
    mycol = mydb["review"]

    event = json.loads(req)
    response = {"time": {"store-review": {"start_time": start}}}

    if set(event["body"].keys()) == arguments:
        response["time"].update(event["time"])
        mycol.insert_one(event["body"])
    else:
        response['body'] = 'Incomplete arguments'

    response["time"]["store-review"]["end_time"] = time()
    return json.dumps(response)
