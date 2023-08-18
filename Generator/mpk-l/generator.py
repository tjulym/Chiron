import json

TAB = "    "

import_codes = """import threading
import multiprocessing as mp
import psutil
import json
import time
import requests
from mpkmemalloc import *
"""

run_codes = """
def run(f, event, index, conn):
    result = f(event)
    conn.send(result)
    conn.close()
"""

MyThread_codes = """
class MyThread(threading.Thread):
    def __init__(self, func, args=()):
        threading.Thread.__init__(self)
        self.func = func
        self.args = args

    def run(self):
        self.result = self.func(*self.args)

    def recv(self):
        try:
            return self.result
        except Exception:
            return None
"""

runt_codes = """
def runt(f, event):
    pkey_thread_mapper()
    result = f(event)
    pymem_reset()
    return result
"""

remote_codes = """
def remote(index, req):
    url = "http://gateway.openfaas.svc.cluster.local:8080/function/workflow-name-wrap%d" % index
    result = requests.post(url, data=req).json()
    return result
"""

def generate_import_fn_code(fn):
    fn_str = fn.replace("-", "_")
    return f'from function.{fn_str}_handler import handle as {fn_str}'

def generate_invoke_code(stage_input, start_index, end_index):
    invoke_codes = ""
    invoke_codes += f"{TAB}ts = []\n"
    invoke_codes += f"{TAB}for i in range({start_index}, {end_index}):\n"
    invoke_codes += f"{TAB*2}ts.append(MyThread(remote, args=(i, {stage_input})))\n\n"

    invoke_codes += f"{TAB}for t in ts:\n"
    invoke_codes += f"{TAB*2}t.start()\n\n"

    return invoke_codes

def generate_fork_process_code(stage_wrap, stage_input, has_invoke):
    fork_codes = ""
    fork_codes += f"{TAB}ps = []\n"
    fork_codes += f"{TAB}parent_conns = []\n\n"

    fns_str = [fn.replace("-", "_") for fn in stage_wrap]
    fork_codes += "%sfuncs = [%s]\n" % (TAB, ", ".join(fns_str))

    fork_codes += f"{TAB}for i, f in enumerate(funcs):\n"
    fork_codes += f"{TAB*2}parent_conn, child_conn = mp.Pipe()\n"
    fork_codes += f"{TAB*2}parent_conns.append(parent_conn)\n"
    fork_codes += f"{TAB*2}ps.append(mp.Process(target=run, args=[f, {stage_input}, i, child_conn]))\n\n"

    fork_codes += f"{TAB}for p in ps:\n"
    fork_codes += f"{TAB*2}p.start()\n\n"

    fork_codes += f"{TAB}for p in ps:\n"
    fork_codes += f"{TAB*2}p.join()\n\n"

    fork_codes += f"{TAB}stage_res = []\n"
    fork_codes += f"{TAB}for parent_conn in parent_conns:\n"
    fork_codes += f"{TAB*2}stage_res.append(parent_conn.recv())\n\n"

    if has_invoke:
        fork_codes += f"{TAB}for t in ts:\n"
        fork_codes += f"{TAB*2}t.join()\n"
        fork_codes += f"{TAB*2}stage_res.extend(t.recv())\n\n"

    fork_codes += f"{TAB}stage_res = json.dumps(stage_res)\n\n"

    return fork_codes

def generate_thread_code(fn, stage_input):
    thread_codes = ""
    fn_str = fn.replace("-", "_")
    thread_codes += f'{TAB}p = MyThread(runt, args=({fn_str}, {stage_input}))\n'
    thread_codes += f'{TAB}p.start()\n'
    thread_codes += f'{TAB}p.join()\n\n'

    thread_codes += f"{TAB}stage_res = p.recv()\n\n"

    return thread_codes

def generate_wrap_code(req):
    try:
        event = json.loads(req)
        workflow_name = event["workflow"]
        wraps = event["wraps"]
        wrap_index = event["wrap_index"]

        is_wrap1 = False
        wrap_index_list = [int(i) for i in wrap_index.split(",")]
        if wrap_index_list[0] == 0 and wrap_index_list[1] == 0:
            is_wrap1 = True

    except Exception as e:
        raise e

    import_funcs = set()

    handle_codes = "def handle(req):\n"

    if is_wrap1:
        handle_codes += f"{TAB}start = time.time()\n\n"
        handle_codes += f"{TAB}pymem_setup_allocators(0)\n\n"

    remote_wrap_index_start = 2

    stage_input = "req"
    for stage_index, stage_wraps in enumerate(wraps):
        print(stage_index, stage_wraps)
        if is_wrap1:
            stage_wrap = stage_wraps[0]
        elif wrap_index_list[0] == stage_index:
            stage_wrap = stage_wraps[wrap_index_list[1]]
        else:
            continue

        print(stage_wrap)

        if is_wrap1 and len(stage_wraps) > 1:
            handle_codes += generate_invoke_code(stage_input, remote_wrap_index_start, remote_wrap_index_start + len(stage_wraps) - 1)

        if len(stage_wrap) > 1:
            handle_codes += generate_fork_process_code(stage_wrap, stage_input, (is_wrap1) and (len(stage_wraps) > 1))
        else:
            handle_codes += generate_thread_code(stage_wrap[0], stage_input)

        for fn in stage_wrap:
            import_funcs.add(fn)

        remote_wrap_index_start += (len(stage_wraps) - 1)

        stage_input = "stage_res"

    if is_wrap1:
        handle_codes += f"{TAB}pymem_reset_pkru()\n"
        handle_codes += (TAB + 'return {"result": stage_res, "time": {"workflow": {"start": start, "end": time.time()}}}' + "\n")
    else:
        handle_codes += f"{TAB}return stage_res"

    import_funcs_code = "\n".join([generate_import_fn_code(fn) for fn in import_funcs])
    local_import_codes = import_codes + import_funcs_code + "\n"
    # print(local_import_codes)
    # print(handle_codes)

    wrap_codes = ""

    wrap_codes += local_import_codes
    wrap_codes += run_codes
    wrap_codes += MyThread_codes
    wrap_codes += runt_codes
    wrap_codes += (remote_codes.replace("workflow-name", workflow_name.lower()) + "\n")
    wrap_codes += handle_codes

    return wrap_codes

if __name__ == '__main__':
    print(generate_wrap_code('{"workflow": "finra50", "wrap_index": "0,0", "wraps": [[["marketdata", "trddate", "trddate", "trddate", "trddate", "lastpx", "lastpx", "lastpx", "lastpx"], ["marketdata", "trddate", "trddate", "trddate", "volume", "volume", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "volume", "volume", "volume", "side"], ["marketdata", "marketdata", "trddate", "lastpx", "volume", "side", "side", "side"], ["marketdata", "marketdata", "lastpx", "lastpx", "lastpx", "volume", "volume", "side"], ["marketdata", "marketdata", "lastpx", "lastpx", "volume", "side", "side", "side"]], [["margin-balance"]]]}'))
    # print(generate_wrap_code('{"workflow": "finra50", "wrap_index": "0,1", "wraps": [[["marketdata", "trddate", "trddate", "trddate", "trddate", "lastpx", "lastpx", "lastpx", "lastpx"], ["marketdata", "trddate", "trddate", "trddate", "volume", "volume", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "volume", "volume", "volume", "side"], ["marketdata", "marketdata", "trddate", "lastpx", "volume", "side", "side", "side"], ["marketdata", "marketdata", "lastpx", "lastpx", "lastpx", "volume", "volume", "side"], ["marketdata", "marketdata", "lastpx", "lastpx", "volume", "side", "side", "side"]], [["margin-balance"]]]}'))
    # print(generate_wrap_code('{"workflow": "finra50", "wrap_index": "0,5", "wraps": [[["marketdata", "trddate", "trddate", "trddate", "trddate", "lastpx", "lastpx", "lastpx", "lastpx"], ["marketdata", "trddate", "trddate", "trddate", "volume", "volume", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "volume", "volume", "volume", "side"], ["marketdata", "marketdata", "trddate", "lastpx", "volume", "side", "side", "side"], ["marketdata", "marketdata", "lastpx", "lastpx", "lastpx", "volume", "volume", "side"], ["marketdata", "marketdata", "lastpx", "lastpx", "volume", "side", "side", "side"]], [["margin-balance"]]]}'))