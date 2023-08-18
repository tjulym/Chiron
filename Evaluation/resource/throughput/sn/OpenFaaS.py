import requests
import threading
import json
import time

compose_post_url = "http://127.0.0.1:31112/function/compose-post"

upload_media_url = "http://127.0.0.1:31112/function/upload-media"
upload_creator_url = "http://127.0.0.1:31112/function/upload-creator"
upload_text_url = "http://127.0.0.1:31112/function/upload-text"
upload_user_mentions_url = "http://127.0.0.1:31112/function/upload-user-mentions"
upload_unique_id_url = "http://127.0.0.1:31112/function/upload-unique-id"

compose_and_upload_url = "http://127.0.0.1:31112/function/compose-and-upload"

post_storage_url = "http://127.0.0.1:31112/function/post-storage"
upload_user_timeline_url = "http://127.0.0.1:31112/function/upload-user-timeline"
upload_home_timeline_url = "http://127.0.0.1:31112/function/upload-home-timeline"

funcs = ["compose-post", "upload-media", "upload-creator", "upload-text", "upload-user-mentions",
         "upload-unique-id", "compose-and-upload", "post-storage", "upload-user-timeline", "upload-home-timeline"]

def post(url, data, l):
    res = requests.post(url, data).text
    l.append(res)

def workflow_OpenFaaS(data):
    start = time.time()    
    compose_res = requests.post(compose_post_url, data=data).text
    
    parallel_res = []
    threads = []
    for url in [upload_user_mentions_url, upload_creator_url, upload_media_url, upload_text_url, upload_unique_id_url]:
        t = threading.Thread(target=post, args=(url, compose_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()
    
    compose_and_upload_res = requests.post(compose_and_upload_url, data=json.dumps(parallel_res)).text
    
    parallel_res = []
    threads = []
    for url in [post_storage_url, upload_home_timeline_url, upload_user_timeline_url]:
        t = threading.Thread(target=post, args=(url, compose_and_upload_res, parallel_res))
        threads.append(t)
    
    for t in threads:
        t.start()
    
    for t in threads:
        t.join()

    return int((time.time() - start) * 1000)
