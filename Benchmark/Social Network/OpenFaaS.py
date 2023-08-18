import requests
import threading
import random
import string
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

def gen_random_string(i):
    choices = string.ascii_letters + string.digits
    return "".join([choices[random.randint(0, len(choices)-1)] for j in range(i)])

def post(url, data, l):
    res = requests.post(url, data).text
    l.append(res)

def generate_data():
    user_index = random.randint(1, 1000)
    
    num_user_mentions = random.randint(1, 5)
    num_urls = random.randint(1, 5)
    num_media = random.randint(1, 4)
    text = ""
    
    user_mentions = []
    for i in range(num_user_mentions):
        while True:
            user_mention_id = random.randint(1, 1000)
            if user_mention_id != user_index and user_mention_id not in user_mentions:
                user_mentions.append(user_mention_id)
                break
    
    text += " ".join(["@username_"+str(i) for i in user_mentions])
    text += " "
    
    for i in range(num_urls):
        text += ("http://"+gen_random_string(64)+" ")
    
    media_ids = []
    media_types = ["png"] * num_media
    for i in range(num_media):
        media_ids.append(gen_random_string(5))
    
    data = {
        "username": "username_" + str(user_index),
        "user_id": user_index,
        "post_type": 0,
        "text": text,
        "media_ids": ",".join(media_ids),
        "media_types": ",".join(media_types)
    }

    return json.dumps(data)


def workflow():
    data = generate_data()
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

    #return int((time.time()-start)*1000)
    
    print("This request uses %d ms" % int((time.time() - start) * 1000))
   
    funcs_time = {}
    for f in funcs:
        funcs_time[f] = -1
    
    try:
        for res in parallel_res:
            res = json.loads(res)
            for k, v in res["time"].items():
                funcs_time[k] = int((v["end_time"] - v["start_time"]) * 1000)
                if funcs_time[k] == 0:
                    funcs_time[k] = round((v["end_time"] - v["start_time"]) * 1000, 2)
                print(k, v["start_time"], v["end_time"])
        print("Details:")
        for f in funcs:
            print("  %s: %s ms" % (f, str(funcs_time[f])))
    except Exception as e:
        raise e

if __name__ == '__main__':
    workflow()
