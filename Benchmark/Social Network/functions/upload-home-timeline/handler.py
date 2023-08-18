import json
import redis
import pymongo
from time import time

home_timeline_redis = "home-timeline-redis.socialnetwork-db.svc.cluster.local"
redis_client = redis.Redis(host=home_timeline_redis, port=6379, decode_responses=True)

sgclient = pymongo.MongoClient("mongodb://social-graph-mongodb.socialnetwork-db.svc.cluster.local:27017/")
sgdb = sgclient['social-graph']
sgcol = sgdb["social-graph"]

def get_followers(user_id):
    followers = []

    user_query = { "user_id": user_id }
    user_doc = sgcol.find(user_query)

    if user_doc.count() > 0:
        j = json.loads(user_doc.next()["followers"])
        if len(j) > 0:
            followers.extend(j.keys())

    return followers
    

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    event = json.loads(req)

    response = {"time": {"upload-home-timeline": {"start_time": start}}}

    user_id = event["body"]["creator"]["user_id"]
    post_id = event["body"]["post_id"]
    user_mentions = event["body"]["user_mentions"]
    
    timestamp = time()

    followers = get_followers(user_id)
    followers.extend(user_mentions)
    followers = set(followers)

    for i in followers:
        redis_client.hset(i, post_id, timestamp)

    response["time"]["upload-home-timeline"]["end_time"] = time()

    return json.dumps(response)
