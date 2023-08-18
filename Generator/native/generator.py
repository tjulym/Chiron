import json

TAB = "    "

import_codes = """import threading
import multiprocessing as mp
import psutil
import json
import time
import requests
"""

run_codes = """
def run(fs, event, index, conn):
    psutil.Process().cpu_affinity([index])
    results = []
    ps = []
    for f in fs:
        ps.append(MyThread(runt, args=[f, event]))
    for p in ps:
        p.start()
    for p in ps:
        p.join()
        results.append(p.recv())

    conn.send(results)
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
    result = f(event)
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

def generate_fork_process_code(stage_wrap, stage_input, start_index):
    fork_codes = ""
    fork_codes += f"{TAB}ps = []\n"
    fork_codes += f"{TAB}parent_conns = []\n\n"

    fns_new_process = []
    for process_fns in stage_wrap[1:]:
        process_fns_str = [fn.replace("-", "_") for fn in process_fns]
        fns_new_process.append("[%s]" % ", ".join(process_fns_str))
    fns_new_process_str = "[%s]" % ", ".join(fns_new_process)

    fork_codes += f"{TAB}ps_fss = {fns_new_process_str}\n"
    fork_codes += f"{TAB}for i, fs in enumerate(ps_fss):\n"
    fork_codes += f"{TAB*2}parent_conn, child_conn = mp.Pipe()\n"
    fork_codes += f"{TAB*2}parent_conns.append(parent_conn)\n"
    fork_codes += f"{TAB*2}ps.append(mp.Process(target=run, args=[fs, {stage_input}, {start_index+1}+i, child_conn]))\n\n"

    fork_codes += f"{TAB}for p in ps:\n"
    fork_codes += f"{TAB*2}p.start()\n\n"

    return fork_codes

def generate_main_process_code(fns, stage_input, start_index):
    main_codes = ""
    fns_str = [fn.replace("-", "_") for fn in fns]
    main_codes += f'{TAB}main_fs = [{", ".join(fns_str)}]\n'
    main_codes += f"{TAB}for f in main_fs:\n"
    main_codes += f"{TAB*2}ts.append(MyThread(runt, args=[f, {stage_input}]))\n\n"

    main_codes += f"{TAB}for t in ts[{start_index}:]:\n"
    main_codes += f"{TAB*2}t.start()\n\n"

    main_codes += f"{TAB}for t in ts:\n"
    main_codes += f"{TAB*2}t.join()\n\n"

    return main_codes

def generate_stage_res_code(num_main_fn, num_invoke, num_fork):
    stage_res_codes = ""
    if num_main_fn == 1 and num_invoke == 0 and num_fork == 0:
        stage_res_codes += f"{TAB}stage_res = ts[0].recv()\n\n"
    else:
        stage_res_codes += f"{TAB}stage_res = []\n"

        if num_fork > 0:
            stage_res_codes += f"{TAB}for parent_conn in parent_conns:\n"
            stage_res_codes += f"{TAB*2}stage_res.extend(parent_conn.recv())\n"

        stage_res_codes += f"{TAB}for t in ts[{num_invoke}:]:\n"
        stage_res_codes += f"{TAB*2}stage_res.append(t.recv())\n"
        if num_invoke > 0:
            stage_res_codes += f"{TAB}for t in ts[:{num_invoke}]:\n"
            stage_res_codes += f"{TAB*2}stage_res.extend(t.recv())\n\n"

        stage_res_codes += f"{TAB}stage_res = json.dumps(stage_res)\n\n"
    return stage_res_codes

def generate_wrap_code(req):
    try:
        event = json.loads(req)
        workflow_name = event["workflow"]
        wraps = event["wraps"]
        num_wraps = event["num_wraps"]
        wrap_index = event["wrap_index"]

        is_wrap1 = False
        wrap_index_list = [int(i) for i in wrap_index.split(",")]
        if wrap_index_list[0] == 0 and wrap_index_list[1] == 0:
            is_wrap1 = True

    except Exception as e:
        raise e

    import_funcs = set()

    if is_wrap1:
        start_index = 0
    else:
        start_index = max([len(stage_wraps[0]) for stage_wraps in wraps])

    handle_codes = "def handle(req):\n"

    if is_wrap1:
        handle_codes += f"{TAB}start = time.time()\n\n"

    remote_wrap_index_start = 2

    for stage_index, stage_wraps in enumerate(wraps):
        if is_wrap1:
            stage_wrap = stage_wraps[0]
        elif wrap_index_list[0] == stage_index:
            stage_wrap = stage_wraps[wrap_index_list[1]]
            for stage_wrap in stage_wraps[1:wrap_index_list[1]]:
                start_index += len(stage_wrap)
        else:
            if len(stage_wraps) > 1:
                for stage_wrap in stage_wraps[1:]:
                    start_index += len(stage_wrap)
            continue

        if not (is_wrap1 and stage_index > 0):
            handle_codes += f"{TAB}start_index = {start_index}\n"
            handle_codes += f"{TAB}psutil.Process().cpu_affinity([{start_index}])\n\n"

        if is_wrap1 and stage_index > 0:
            stage_input = "stage_res"
        else:
            stage_input = "req"

        if is_wrap1 and len(stage_wraps) > 1:
            handle_codes += generate_invoke_code(stage_input, remote_wrap_index_start, remote_wrap_index_start + len(stage_wraps) - 1)
        else:
            handle_codes += f"{TAB}ts = []\n"

        if len(stage_wrap) > 1:
            handle_codes += generate_fork_process_code(stage_wrap, stage_input, start_index)

        if is_wrap1:
            handle_codes += generate_main_process_code(stage_wrap[0], stage_input, len(stage_wraps)-1)
        else:
            handle_codes += generate_main_process_code(stage_wrap[0], stage_input, 0)

        if len(stage_wrap) > 1:
            handle_codes += f"{TAB}for p in ps:\n"
            handle_codes += f"{TAB*2}p.join()\n\n"

        if is_wrap1:
            handle_codes += generate_stage_res_code(len(stage_wrap[0]), len(stage_wraps) - 1, len(stage_wrap) - 1)
        else:
            handle_codes += generate_stage_res_code(len(stage_wrap[0]), 0, len(stage_wrap) - 1)

        for process_index, process_fns in enumerate(stage_wrap):
            for fn in process_fns:
                import_funcs.add(fn)

        remote_wrap_index_start += (len(stage_wraps) - 1)

    if is_wrap1:
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
    # print(generate_wrap_code('{"workflow": "finra100", "wrap_index": "0,0", "num_wraps": 2, "wraps": [[[["marketdata", "trddate", "trddate", "trddate", "lastpx", "lastpx", "lastpx", "lastpx", "lastpx", "volume"], ["marketdata", "marketdata", "trddate", "lastpx", "lastpx", "side", "side", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "lastpx", "side", "side", "side", "side"], ["marketdata", "marketdata", "trddate", "lastpx", "lastpx", "lastpx", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "lastpx", "volume", "volume", "side", "side"], ["marketdata", "lastpx", "volume", "volume", "volume", "volume", "volume", "volume", "volume"]], [["marketdata", "marketdata", "trddate", "trddate", "lastpx", "lastpx", "volume", "volume", "side"], ["marketdata", "marketdata", "trddate", "trddate", "trddate", "volume", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "lastpx", "lastpx", "volume", "volume", "side"], ["trddate", "marketdata", "trddate", "side", "volume", "marketdata", "lastpx", "lastpx", "volume"], ["side", "marketdata", "side", "trddate", "marketdata", "lastpx", "side", "volume", "trddate"]]], [[["margin-balance"]]]]}'))
    # print(generate_wrap_code('{"workflow": "finra100","wrap_index": "0,1", "num_wraps": 2, "wraps": [[[["marketdata", "trddate", "trddate", "trddate", "lastpx", "lastpx", "lastpx", "lastpx", "lastpx", "volume"], ["marketdata", "marketdata", "trddate", "lastpx", "lastpx", "side", "side", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "lastpx", "side", "side", "side", "side"], ["marketdata", "marketdata", "trddate", "lastpx", "lastpx", "lastpx", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "lastpx", "volume", "volume", "side", "side"], ["marketdata", "lastpx", "volume", "volume", "volume", "volume", "volume", "volume", "volume"]], [["marketdata", "marketdata", "trddate", "trddate", "lastpx", "lastpx", "volume", "volume", "side"], ["marketdata", "marketdata", "trddate", "trddate", "trddate", "volume", "volume", "side", "side"], ["marketdata", "marketdata", "trddate", "trddate", "lastpx", "lastpx", "volume", "volume", "side"], ["trddate", "marketdata", "trddate", "side", "volume", "marketdata", "lastpx", "lastpx", "volume"], ["side", "marketdata", "side", "trddate", "marketdata", "lastpx", "side", "volume", "trddate"]]], [[["margin-balance"]]]]}'))

    # print(generate_wrap_code('{"workflow": "finra5", "wrap_index": "0,0", "num_wraps": 1, "wraps": [[[["marketdata", "trddate", "lastpx", "volume", "side"]]], [[["margin-balance"]]]]}'))

    print(generate_wrap_code('{"workflow": "sn", "wrap_index": "0,0", "num_wraps": 1, "wraps": [[[["compose-post"]]], [[["upload-creator", "upload-user-mentions", "upload-text", "upload-unique-id", "upload-media"]]], [[["compose-and-upload"]]], [[["upload-home-timeline", "upload-user-timeline", "post-storage"]]]]}'))

    # print(generate_wrap_code('{"workflow": "SLApp", "wrap_index": "0,0", "num_wraps": 1, "wraps": [[[["factorial", "network-io"], ["fibonacci", "disk-io"]]], [[["pi", "pbkdf2"], ["network-io"]]]]}'))