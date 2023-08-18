import json
import time

import pymongo
import memcache

mongo_url = "mongodb://user-mongodb.socialnetwork-db.svc.cluster.local:27017/"
memcache_url = "user-memcached.socialnetwork-db.svc.cluster.local:11211"

mc = memcache.Client([memcache_url])
"""
myclient = pymongo.MongoClient(mongo_url, connect=False)
mydb = myclient['user']
mycol = mydb["user"]
"""

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    myclient = pymongo.MongoClient(mongo_url)
    mydb = myclient['user']
    mycol = mydb["user"]

    event = json.loads(req)

    response = {"time": {"upload-creator": {"start_time": start}}}

    username = event["body"]["username"]
    user_id = str(event["body"]["user_id"])

    user_id_2 = None
    mmc_user_id = mc.get(username+":user_id")
    if mmc_user_id != None:
        user_id_2 = mmc_user_id
    else:
        myquery = { "username": username }
        mydoc = mycol.find(myquery)
        if mydoc.count() > 0:
            it = mydoc.next()
            if "user_id" in it.keys():
                user_id_2 = it["user_id"]
                mc.set(username+":user_id", user_id_2)

    if user_id == user_id_2:
        response["body"] = {"creator": {"username": username, "user_id": user_id}}
    else:
        response["body"] = {"creator": {"username": username, "user_id": user_id_2}}

    response["time"].update(event["time"])

    response["time"]["upload-creator"]["end_time"] = time.time()

    return json.dumps(response)
