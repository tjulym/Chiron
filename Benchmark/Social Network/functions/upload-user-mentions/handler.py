import json
import time
import pymongo
import re
import memcache

mongo_url = "mongodb://user-mongodb.socialnetwork-db.svc.cluster.local:27017/"
memcache_url = "user-memcached.socialnetwork-db.svc.cluster.local:11211"

mc = memcache.Client([memcache_url])
myclient = pymongo.MongoClient(mongo_url)
mydb = myclient['user']
mycol = mydb["user"]

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time.time()

    event = json.loads(req)

    response = {"time": {"upload-user-mentions": {"start_time": start}}}

    text = event["body"]["text"]

    users_pattern = re.compile(r'@[a-zA-Z0-9-_]+')
    users_match = users_pattern.findall(text)
    users = []
    for m in users_match:
        users.append(m[1:])

    user_ids = []
    for username in users:
        mmc_user_id = mc.get(username+":user_id")
        if mmc_user_id != None:
            user_id = mmc_user_id
        else:
            myquery = { "username": username }
            mydoc = mycol.find(myquery)
            if mydoc.count() > 0:
                it = mydoc.next()
                if "user_id" in it.keys():
                    user_id = it["user_id"]
                    mc.set(username+":user_id", user_id)
        user_ids.append(user_id)

    response["body"] = {"user_mentions": user_ids}
    response["time"].update(event["time"])
    
    response["time"]["upload-user-mentions"]["end_time"] = time.time()

    return json.dumps(response)
    
