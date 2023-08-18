import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/sn-wrap"

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]

CPUs = [10,  5,   5,   1,   5,   2,  5,  2]

times = 10

th_time = 10

TIME_FLAG = True

def timer():
    global TIME_FLAG
    time.sleep(th_time)
    TIME_FLAG = False

def gen_random_string(i):
    choices = string.ascii_letters + string.digits
    return "".join([choices[random.randint(0, len(choices)-1)] for j in range(i)])

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

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f sn-wrap.yml"
    else:
        cmd = "faas-cli deploy -f sn-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../../deploy.py sn-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_improvement(all_ths):
    expect_ths = [1344.0, 2080.0, 2592.0, 33200, 6000.0, 16800.0, 2032.0, 4120.0]

    print("===improvement===")

    for index, method in enumerate(methods):
        if index == 3 or index == 5 or index == 7:
            continue
        if index < 4:
            expect_improvement = expect_ths[3]/expect_ths[index] - 1
            actual_improvement = all_ths[3]/all_ths[index]  - 1
        elif index == 4:
            expect_improvement = expect_ths[5]/expect_ths[index] - 1
            actual_improvement = all_ths[5]/all_ths[index] - 1
        elif index == 6:
            expect_improvement = expect_ths[7]/expect_ths[index] - 1
            actual_improvement = all_ths[7]/all_ths[index] - 1

        print("%s: expect %.2f%%, actual %.2f%%" % (method, (expect_improvement*100), (actual_improvement*100)))

def get_ths():
    global TIME_FLAG
    init()

    all_ths = []

    for index, method in enumerate(methods):
        if index > 0:
            deploy(index)

        n = 100
        reqs = []
        for i in range(n):
            reqs.append(generate_data())

        count = 0
        timer_th = threading.Thread(target=timer)
        timer_th.start()

        while TIME_FLAG:
            if index > 0:
                res = requests.post(url, data=reqs[index % n]).text
            else:
                res = workflow_OpenFaaS(reqs[index % n])
            count += 1

        timer_th.join()

        print("%s: %.2f reqs in 1s with %d CPUs" % (method, count * 1.0 / th_time, CPUs[index]))

        TIME_FLAG = True

        all_ths.append(count * 80.0 / CPUs[index])

    get_improvement(all_ths)

    init()

if __name__ == '__main__':
    get_ths()