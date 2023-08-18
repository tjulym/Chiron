import requests
import threading
import json
import time

compose_review_url = "http://127.0.0.1:31112/function/compose-review"
upload_user_id_url = "http://127.0.0.1:31112/function/upload-user-id"
upload_movie_id_url = "http://127.0.0.1:31112/function/upload-movie-id"
mr_upload_text_url = "http://127.0.0.1:31112/function/mr-upload-text"
mr_upload_unique_id_url = "http://127.0.0.1:31112/function/mr-upload-unique-id"
mr_compose_and_upload_url = "http://127.0.0.1:31112/function/mr-compose-and-upload"
store_review_url = "http://127.0.0.1:31112/function/store-review"
upload_user_review_url = "http://127.0.0.1:31112/function/upload-user-review"
upload_movie_review_url = "http://127.0.0.1:31112/function/upload-movie-review"

funcs = ["compose-review", "upload-user-id", "upload-movie-id", "mr-upload-text", "mr-upload-unique-id", 
    "mr-compose-and-upload", "store-review", "upload-user-review", "upload-movie-review"]

def post(url, data, l):
    res = requests.post(url, data).text
    l.append(res)

def workflow_OpenFaaS(review):
    start = time.time()   
    
    compose_res = requests.post(compose_review_url, data=review).text
    
    parallel_res = []
    threads = []
    for url in [upload_user_id_url, upload_movie_id_url, mr_upload_text_url, mr_upload_unique_id_url]:
        t = threading.Thread(target=post, args=(url, compose_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    compose_and_upload_res = requests.post(mr_compose_and_upload_url, data=json.dumps(parallel_res)).text
    
    parallel_res = []
    threads = []
    for url in [store_review_url, upload_user_review_url, upload_movie_review_url]:
        t = threading.Thread(target=post, args=(url, compose_and_upload_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

    return int((time.time() - start) * 1000)
