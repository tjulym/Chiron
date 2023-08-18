from time import time
import pymongo
import json

"""
myclient = pymongo.MongoClient("mongodb://movie-review-mongodb.movie-reviewing.svc.cluster.local:27017/", connect=False)
mydb = myclient["movie-review"]
mycol = mydb["movie-review"]
"""

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    start = time()

    myclient = pymongo.MongoClient("mongodb://movie-review-mongodb.movie-reviewing.svc.cluster.local:27017/")
    mydb = myclient["movie-review"]
    mycol = mydb["movie-review"]

    event = json.loads(req)
    response = {"time": {"upload-movie-review": {"start_time": start}}}

    try:
        movie_id = event["body"]["movie_id"]
        review_id = event["body"]["review_id"]
        timestamp = event["body"]["timestamp"]

        myquery = {"movie_id": movie_id}
        mydoc = mycol.find(myquery)
        if mydoc.count() > 0:
            reviews = json.loads(mydoc.next()["reviews"])
            reviews.append((review_id, timestamp))
            reviews_update = {"$set": {"reviews": json.dumps(reviews)}}
            mycol.update_one(myquery, reviews_update)
        else:
            body = {"movie_id": movie_id, "reviews": json.dumps([(review_id, timestamp)])}
            mycol.insert_one(body)
    except Exception as e:
        response['body'] = 'Incomplete arguments'

    response["time"]["upload-movie-review"]["end_time"] = time()
    return json.dumps(response)
