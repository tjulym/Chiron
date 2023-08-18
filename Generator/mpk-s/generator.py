import json

TAB = "    "

import_codes = """import threading
import multiprocessing as mp
import psutil
import json
import time
from mpkmemalloc import *
"""

run_codes = """
def run(f, event, index, conn):
    psutil.Process().cpu_affinity([index])
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

def generate_import_fn_code(fn):
    fn_str = fn.replace("-", "_")
    return f'from function.{fn_str}_handler import handle as {fn_str}'

def generate_fork_process_code(stage_fns, stage_indexs, stage_input):
    fork_codes = ""
    fork_codes += f"{TAB}ps = []\n"
    fork_codes += f"{TAB}parent_conns = []\n"
    stage_fns_str = [fn.replace("-", "_") for fn in stage_fns]
    fork_codes += "%sfuncs = [%s]\n" % (TAB, ", ".join(stage_fns_str))
    fork_codes += "%sindexs = [%s]\n" % (TAB, ", ".join([str(i) for i in stage_indexs]))

    fork_codes += f"{TAB}for i, f in zip(indexs, funcs):\n"
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
        indexs = event["indexs"]
    except Exception as e:
        raise e

    import_funcs = set()

    start_index = 0

    handle_codes = "def handle(req):\n"

    handle_codes += f"{TAB}start = time.time()\n\n"
    handle_codes += f"{TAB}pymem_setup_allocators(0)\n\n"
    handle_codes += f"{TAB}psutil.Process().cpu_affinity([{start_index}])\n\n"

    stage_input = "req"
    for fns, fn_indexs in zip(wraps, indexs):
        if len(fns) > 1:
            handle_codes += generate_fork_process_code(fns, fn_indexs, stage_input)
        else:
            handle_codes += generate_thread_code(fns[0], stage_input)

        for fn in fns:
            import_funcs.add(fn)

        stage_input = "stage_res"

    handle_codes += f"{TAB}pymem_reset_pkru()\n\n"
    handle_codes += (TAB + 'return {"result": stage_res, "time": {"workflow": {"start": start, "end": time.time()}}}' + "\n")


    import_funcs_code = "\n".join([generate_import_fn_code(fn) for fn in import_funcs])
    local_import_codes = import_codes + import_funcs_code + "\n"
    # print(local_import_codes)
    # print(handle_codes)

    wrap_codes = ""

    wrap_codes += local_import_codes
    wrap_codes += run_codes
    wrap_codes += MyThread_codes
    wrap_codes += runt_codes
    wrap_codes += handle_codes

    return wrap_codes

if __name__ == '__main__':
    print(generate_wrap_code('{"workflow": "finra5", "wraps": [["marketdata", "trddate", "lastpx", "volume", "side"], ["margin-balance"]], "indexs": [[0, 0, 0, 0, 0], [0]]}'))

    # print(generate_wrap_code('{"workflow": "sn", "wraps": [["compose-post"], ["upload-user-mentions", "upload-creator", "upload-text", "upload-unique-id", "upload-media"], ["compose-and-upload"], ["upload-home-timeline", "upload-user-timeline", "post-storage"]], "indexs": [[0], [1, 0, 1, 0, 1], [0], [1, 0, 1]]}'))