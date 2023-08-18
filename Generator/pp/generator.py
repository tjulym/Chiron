import json

TAB = "    "

import_codes = """from concurrent.futures import ProcessPoolExecutor
import psutil
import json
import time
"""

run_codes = """
def run(f, event, index):
    psutil.Process().cpu_affinity([index])
    result = f(event)
    return result

"""

pool_def_code = "Pools = ProcessPoolExecutor(max_workers=max-parallelism)\n"

def generate_import_fn_code(fn):
    fn_str = fn.replace("-", "_")
    return f'from function.{fn_str}_handler import handle as {fn_str}'

def generate_parallel_code(stage_fns, stage_indexs, stage_input):
    parallel_code = ""
    parallel_code += f"{TAB}ps = []\n"
    stage_fns_str = [fn.replace("-", "_") for fn in stage_fns]
    parallel_code += "%sfuncs = [%s]\n" % (TAB, ", ".join(stage_fns_str))
    parallel_code += "%sindexs = [%s]\n" % (TAB, ", ".join([str(i) for i in stage_indexs]))

    parallel_code += f"{TAB}for i, f in zip(indexs, funcs):\n"
    parallel_code += f"{TAB*2}ps.append(Pools.submit(run, f, {stage_input}, i))\n\n"

    parallel_code += f"{TAB}stage_res = []\n"
    parallel_code += f"{TAB}for p in ps:\n"
    parallel_code += f"{TAB*2}stage_res.append(p.result())\n\n"

    parallel_code += f"{TAB}stage_res = json.dumps(stage_res)\n\n"

    return parallel_code

def generate_sequential_code(fn, stage_input, start_index):
    sequential_code = ""
    fn_str = fn.replace("-", "_")
    sequential_code += f'{TAB}p = Pools.submit(run, {fn_str}, {stage_input}, {start_index})\n'

    sequential_code += f"{TAB}stage_res = p.result()\n\n"

    return sequential_code

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
    handle_codes += f"{TAB}psutil.Process().cpu_affinity([{start_index}])\n\n"

    stage_input = "req"
    max_parallelism = 1
    for fns, fn_indexs in zip(wraps, indexs):
        if len(fns) > 1:
            handle_codes += generate_parallel_code(fns, fn_indexs, stage_input)
            max_parallelism = max(max_parallelism, len(fns))
        else:
            handle_codes += generate_sequential_code(fns[0], stage_input, start_index)

        for fn in fns:
            import_funcs.add(fn)

        stage_input = "stage_res"

    handle_codes += (TAB + 'return {"result": stage_res, "time": {"workflow": {"start": start, "end": time.time()}}}' + "\n")


    import_funcs_code = "\n".join([generate_import_fn_code(fn) for fn in import_funcs])
    local_import_codes = import_codes + import_funcs_code + "\n"
    # print(local_import_codes)
    # print(handle_codes)

    wrap_codes = ""

    wrap_codes += local_import_codes + "\n"
    wrap_codes += (pool_def_code.replace("max-parallelism", str(max_parallelism)))
    wrap_codes += run_codes
    wrap_codes += handle_codes

    return wrap_codes

if __name__ == '__main__':
    # print(generate_wrap_code('{"workflow": "finra5", "wraps": [["marketdata", "trddate", "lastpx", "volume", "side"], ["margin-balance"]], "indexs": [[0, 0, 0, 0, 0], [0]]}'))

    print(generate_wrap_code('{"workflow": "sn", "wraps": [["compose-post"], ["upload-user-mentions", "upload-creator", "upload-text", "upload-unique-id", "upload-media"], ["compose-and-upload"], ["upload-home-timeline", "upload-user-timeline", "post-storage"]], "indexs": [[0], [1, 0, 0, 1, 1], [0], [1, 0, 0]]}'))