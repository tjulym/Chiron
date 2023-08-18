import requests
import threading
import random
import string
import json
import time
import subprocess

from OpenFaaS import workflow_OpenFaaS

url = "http://127.0.0.1:31112/function/mr-wrap"

methods = ["OpenFaaS", "SAND", "Faastlane", "Chiron", "Faastlane-P", "Chiron-P", "Faastlane-M", "Chiron-M"]

times = 10

def gen_random_string(i):
    choices = string.ascii_letters + string.digits
    return "".join([choices[random.randint(0, len(choices)-1)] for j in range(i)])

movie_titles = []
with open("movie_titles.csv", "r") as f:
    movie_titles = f.readlines()

def generate_data():
    user_index = str(random.randint(1, 1000))
    review = {
        "username": "username_" + user_index,
        "password": "password_" + user_index,
        "title": movie_titles[random.randint(0, len(movie_titles)-1)].strip(),
        "rating": random.randint(0, 10),
        "text": gen_random_string(256) 
    }

    return json.dumps(review)

def init(not_mpk=True):
    if not_mpk:
        cmd = "faas-cli deploy -f mr-wrap.yml"
    else:
        cmd = "faas-cli deploy -f mr-wrap-mpk.yml"
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def deploy(index):
    file_path = f"wraps/{methods[index]}.py"

    if index == 6:
        init(False)

    cmd = "python3 ../../deploy.py mr-wrap %s" % file_path
    subprocess.check_output(cmd, shell=True).strip()
    time.sleep(5)

def get_improvement(all_lats):
    expect_lats = [65,  71, 53,  30,  22, 22, 71,  74]

    print("===improvement===")

    for index, method in enumerate(methods):
        if index == 3 or index == 5 or index == 7:
            continue
        if index < 4:
            expect_improvement = 1 - expect_lats[3]/expect_lats[index]
            actual_improvement = 1 - all_lats[3]/all_lats[index]
        elif index == 4:
            expect_improvement = 1 - expect_lats[5]/expect_lats[index]
            actual_improvement = 1 - all_lats[5]/all_lats[index]
        elif index == 6:
            expect_improvement = 1 - expect_lats[7]/expect_lats[index]
            actual_improvement = 1 - all_lats[7]/all_lats[index]

        print("%s: expect %.2f%%, actual %.2f%%" % (method, (expect_improvement*100), (actual_improvement*100)))

def get_lats():
    init()

    all_lats = []

    for index, method in enumerate(methods):
        lats = []
        if index > 0:
            deploy(index)
            for i in range(times+1):
                data = generate_data()
                res = requests.post(url, data=data).text
                res_j = json.loads(res)
                lats.append((res_j["time"]["workflow"]["end"] - res_j["time"]["workflow"]["start"])*1000)
        else:
            for i in range(times+1):
                data = generate_data()
                lats.append(workflow_OpenFaaS(data))

        avg_lat = sum(lats[1:])/(len(lats)-1)
        print("%s: %f" % (method, avg_lat))
        all_lats.append(avg_lat)

    get_improvement(all_lats)

    init()

if __name__ == '__main__':
    get_lats()