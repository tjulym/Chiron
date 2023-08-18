import sys
import subprocess
import threading

from invoker import generate_req, invoke_workflow
from extracter import get_timeline

sn_funcs = ["compose-post", "upload-media", "upload-creator", "upload-text", "upload-user-mentions", "upload-unique-id", 
    "compose-and-upload", "post-storage", "upload-user-timeline", "upload-home-timeline"]

mr_funcs = ["compose-review", "upload-user-id", "upload-movie-id", "mr-upload-text", "mr-upload-unique-id", 
    "mr-compose-and-upload", "store-review", "upload-user-review", "upload-movie-review"]

finra_funcs = ["marketdata", "lastpx", "side", "trddate", "volume", "margin-balance"]

SLApp_funcs = ["disk-io", "factorial", "fibonacci", "pbkdf2", "pi", "network-io"]

class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def get_result(self):
        try:
            return self.result
        except Exception:
            return None

def get_workflow_name(func_name):
    if func_name in sn_funcs:
        return "sn"
    elif func_name in mr_funcs:
        return "mr"
    elif func_name in finra_funcs:
        return "finra"
    elif func_name in SLApp_funcs:
        return "SLApp"

    return None

def get_pid(func_name):
    cmd = "docker top `docker ps | grep %s_%s- | awk '{print $1}'` | grep index.py | awk '{print $2}'" % (func_name, func_name)
    pid = subprocess.check_output(cmd, shell=True).strip()
    try:
       return str(int(pid))
    except Exception as e:
       raise e

def profile(target_func, pid):
    cmd = ["strace", "-f", "-ttt", "-T", "-o", "straces/%s.csv" % target_func, "-p", pid]
    try:
        subprocess.run(cmd, timeout=1)
    except subprocess.TimeoutExpired:
        print("timeout")

if __name__ == '__main__':
    try:
        func_name = sys.argv[1]
    except Exception as e:
        raise e

    workflow_name = get_workflow_name(func_name)
    pid = get_pid(func_name)

    warm_req = generate_req(workflow_name)
    warm_res = invoke_workflow(workflow_name, func_name, warm_req)

    req = generate_req(workflow_name)
    start_solo, end_solo = invoke_workflow(workflow_name, func_name, req)

    req2 = generate_req(workflow_name)
    invoker_thread = MyThread(invoke_workflow, args=(workflow_name, func_name, req2))

    profile_thread = threading.Thread(target=profile, args=(func_name, pid))

    profile_thread.start()
    invoker_thread.start()

    invoker_thread.join()
    profile_thread.join()

    res = invoker_thread.get_result()

    get_timeline(func_name, res[0], res[1], end_solo - start_solo)

    print("Solo-run latency: %f ms" % (end_solo - start_solo))
    print("Strace latency: %f ms" % (res[1] - res[0]))