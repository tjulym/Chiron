from time import time
import pymongo
import memcache
import json

mongo_url = "mongodb://user-mongodb.movie-reviewing.svc.cluster.local:27017/"
memcache_url = "user-memcached.movie-reviewing.svc.cluster.local:11211"

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
    start = time()

    myclient = pymongo.MongoClient(mongo_url)
    mydb = myclient['user']
    mycol = mydb["user"]

    event = json.loads(req)
    body = ''
    username = ''    
    response = {"time": {"upload-user-id": {"start_time": start}}}
    try:
        username = event["body"]["username"]
    except Exception as e:
        body = 'Incomplete arguments'

    if username:
        user_id = -1
        mmc_user_id = mc.get(username+":user_id")
        if mmc_user_id != None:
            user_id = mmc_user_id
            body = {"user_id": user_id}
        else:
            myquery = { "username": username }
            mydoc = mycol.find(myquery)
            if mydoc.count() > 0:
                it = mydoc.next()
                user_id = it["user_id"]
                body = {"user_id": user_id}
                mc.set(username+":user_id", user_id)
            else:
                body = 'No user ' + username

    response["body"] = body

    response["time"]["upload-user-id"]["end_time"] = time()
    return json.dumps(response)
