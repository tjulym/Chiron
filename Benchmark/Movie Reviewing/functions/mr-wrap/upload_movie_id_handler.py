from time import time
import pymongo
import memcache
import json
import hashlib

mongo_url = "mongodb://movie-id-mongodb.movie-reviewing.svc.cluster.local:27017/"
memcache_url = "movie-id-memcached.movie-reviewing.svc.cluster.local:11211"

mc = memcache.Client([memcache_url])

"""
myclient = pymongo.MongoClient(mongo_url, connect=False)
mydb = myclient['movie-id']
mycol = mydb["movie-id"]
"""

def hash_key(title):
    m = hashlib.md5()
    m.update(title.encode("utf-8"))
    return m.hexdigest()

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    myclient = pymongo.MongoClient(mongo_url)
    mydb = myclient['movie-id']
    mycol = mydb["movie-id"]

    event = json.loads(req)
    body = ''
    title = ''
    title_hash = ''
    rating = -1
    response = {"time": {"upload-movie-id": {"start_time": start}}}
    try:
        title = event["body"]["title"]
        title_hash = hash_key(title)
        rating = int(event["body"]["rating"])
    except Exception as e:
        response['body'] = 'Incomplete arguments'

    if title and rating > -1:
        movie_id = ''
        mmc_movie_id = mc.get(title_hash)
        if mmc_movie_id != None:
            movie_id = mmc_movie_id
            response["body"] = {"movie_id": movie_id, 'rating': rating}
        else:
            myquery = { "title": title }
            mydoc = mycol.find(myquery)
            if mydoc.count() > 0:
                it = mydoc.next()
                movie_id = it["movie_id"]
                response["body"] = {"movie_id": movie_id, 'rating': rating}
                mc.set(title_hash, movie_id)
            else:
                response["body"] = 'No movie ' + title

    response["time"]["upload-movie-id"]["end_time"] = time()
    return json.dumps(response)
