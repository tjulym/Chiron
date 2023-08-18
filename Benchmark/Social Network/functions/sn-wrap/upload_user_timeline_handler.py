import pymongo
import redis
import json
from time import time

user_timeline_mongodb = "mongodb://user-timeline-mongodb.socialnetwork-db.svc.cluster.local:27017/"
user_timeline_redis = "user-timeline-redis.socialnetwork-db.svc.cluster.local"
"""
myclient = pymongo.MongoClient(user_timeline_mongodb, connect=False)
mydb = myclient['user-timeline']
mycol = mydb["user-timeline"]
"""
redis_client = redis.Redis(host=user_timeline_redis, port=6379, decode_responses=True)

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()
    myclient = pymongo.MongoClient(user_timeline_mongodb)
    mydb = myclient['user-timeline']
    mycol = mydb["user-timeline"]

    event = json.loads(req)

    response = {"time": {"upload-user-timeline": {"start_time": start}}}

    user_id = event["body"]["creator"]["user_id"]
    post_id = event["body"]["post_id"]
    timestamp = time()

    myquery = { "user_id": user_id }
    mydoc = mycol.find(myquery)

    if mydoc.count() == 0:
        posts_j = {}
        posts_j[post_id] = timestamp
        mydict = {"user_id": user_id, "posts": json.dumps(posts_j)}
        mycol.insert_one(mydict)
    else:
        posts_j = json.loads(mydoc.next()["posts"])
        posts_j[post_id] = timestamp
        posts_update = {"$set": {"posts": json.dumps(posts_j)}}
        mycol.update_one(myquery, posts_update)

    redis_client.hset(user_id, post_id, timestamp)

    response["time"]["upload-user-timeline"]["end_time"] = time()

    return json.dumps(response)
