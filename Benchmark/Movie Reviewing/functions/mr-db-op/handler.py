import pymongo
import json
import random
import string
import hashlib

cast_info_client = pymongo.MongoClient("mongodb://cast-info-mongodb.movie-reviewing.svc.cluster.local:27017/")
cast_info_db = cast_info_client['cast-info']
cast_info_col = cast_info_db["cast-info"]

movie_info_client = pymongo.MongoClient("mongodb://movie-info-mongodb.movie-reviewing.svc.cluster.local:27017/")
movie_info_db = movie_info_client['movie-info']
movie_info_col = movie_info_db["movie-info"]

plot_client = pymongo.MongoClient("mongodb://plot-mongodb.movie-reviewing.svc.cluster.local:27017/")
plot_db = plot_client['plot']
plot_col = plot_db["plot"]

movie_id_client = pymongo.MongoClient("mongodb://movie-id-mongodb.movie-reviewing.svc.cluster.local:27017/")
movie_id_db = movie_id_client['movie-id']
movie_id_col = movie_id_db["movie-id"]

user_client = pymongo.MongoClient("mongodb://user-mongodb.movie-reviewing.svc.cluster.local:27017/")
user_db = user_client['user']
user_col = user_db["user"]

review_client = pymongo.MongoClient("mongodb://review-storage-mongodb.movie-reviewing.svc.cluster.local:27017/")
review_db = review_client["review"]
review_col = review_db["review"]

movie_review_client = pymongo.MongoClient("mongodb://movie-review-mongodb.movie-reviewing.svc.cluster.local:27017/")
movie_review_db = movie_review_client["movie-review"]
movie_review_col = movie_review_db["movie-review"]

user_review_client = pymongo.MongoClient("mongodb://user-review-mongodb.movie-reviewing.svc.cluster.local:27017/")
user_review_db = user_review_client["user-review"]
user_review_col = user_review_db["user-review"]

root_dir = "/home/app/function/"

def gen_random_string(i):
    return "".join(random.sample(string.ascii_letters + string.digits, i))

def get_hash256(s):
    hash256 = hashlib.sha256()
    hash256.update(s.encode("utf-8"))
    return hash256.hexdigest()

def write_cast_info():
    with open(root_dir + "datasets/casts.json", 'r') as cast_file:
        raw_casts = json.load(cast_file)
    #idx = 0
    casts = []
    for raw_cast in raw_casts:
        try:
            cast = dict()
            cast["cast_info_id"] = raw_cast["id"]
            cast["name"] = raw_cast["name"]
            cast["gender"] = True if raw_cast["gender"] == 2 else False
            cast["intro"] = raw_cast["biography"]
            #cast_info_col.insert_one(cast)
            #idx += 1
            casts.append(cast)
        except:
            return "Warning: cast info missing!"

    cast_info_col.insert_many(casts)
    #return str(idx) + " casts finished"
    return str(len(casts)) + " casts finished"

def write_movie_info():
    with open(root_dir + "datasets/movies.json", 'r') as movie_file:
        raw_movies = json.load(movie_file)
    #idx = 0
    movies = []
    plots = []
    for raw_movie in raw_movies:
        movie = dict()
        casts = list()
        movie["movie_id"] = str(raw_movie["id"])
        movie["title"] = raw_movie["title"]
        movie_id_col.insert_one(movie)
        movie["plot_id"] = raw_movie["id"]
        for raw_cast in raw_movie["cast"]:
            try:
                cast = dict()
                cast["cast_id"] = raw_cast["cast_id"]
                cast["character"] = raw_cast["character"]
                cast["cast_info_id"] = raw_cast["id"]
                casts.append(cast)
            except:
                return ("Warning: cast info missing in writing movie info!")
        movie["casts"] = casts
        movie["thumbnail_ids"] = [raw_movie["poster_path"]]
        movie["photo_ids"] = []
        movie["video_ids"] = []
        movie["avg_rating"] = raw_movie["vote_average"]
        movie["num_rating"] = raw_movie["vote_count"]
        #movie_info_col.insert_one(movie)
        movies.append(movie)

        plot = dict()
        plot["plot_id"] = raw_movie["id"]
        plot["plot"] = raw_movie["overview"]
        #plot_col.insert_one(plot)
        plots.append(plot)
        #idx += 1

    movie_info_col.insert_many(movies)
    plot_col.insert_many(plots)

    #return str(idx) + " movies finished"
    return str(len(movies)) + " movies finished"

def register_users():
    users = []
    for i in range(1, 1001):
        idx = str(i)
        user = {"first_name": "first_name_"+idx, 
               "last_name": "last_name_"+idx, 
               "username": "username_"+idx, 
               "user_id": int(idx)}
        user["salt"] = gen_random_string(32)
        user["password"] = get_hash256("password_"+idx+user["salt"])
        #user_col.insert_one(user)
        users.append(user)
    user_col.insert_many(users)
    return "1000 users register"

def handle(req):
    """handle a request to the function
    Args:
        req (str): request body
    """
    result = ''
    if req == "1":
        cast_info_col.drop()
        movie_id_col.drop()
        movie_info_col.drop()
        plot_col.drop()
        user_col.drop()
        result += (write_cast_info() + "\n")
        result += (write_movie_info() + "\n")
        result += (register_users() + "\n")
    elif req == "0":
        review_col.drop() 
        movie_review_col.drop() 
        user_review_col.drop() 
        result += "clear\n"

    return result
