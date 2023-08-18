import json
from CFS import predict as threads_predictor, TIMELINE_DICT

# FUNC_EXEC_TIMES = {
#     "compose-post": 0.121996,
#     "upload-user-mentions": 9.765100,
#     "upload-creator": 8.815116,
#     "upload-media": 0.380701,
#     "upload-text": 1.637130,
#     "upload-unique-id": 0.651283,
#     "compose-and-upload": 0.320979,
#     "post-storage": 12.879182,
#     "upload-home-timeline": 19.059915,
#     "upload-user-timeline": 16.112567,
#     "compose-review": 0.107390,
#     "upload-user-id": 8.396033,
#     "upload-movie-id": 8.539929,
#     "mr-upload-text": 0.319250,
#     "mr-upload-unique-id": 0.605604,
#     "mr-compose-and-upload": 0.230004,
#     "store-review": 12.117567,
#     "upload-user-review": 14.946811,
#     "upload-movie-review": 15.873351,
#     "marketdata": 92,
#     "lastpx": 0.735458,
#     "side": 0.722307,
#     "trddate": 0.772194,
#     "volume": 0.730984,
#     "margin-balance": 0.807867,
#     "factorial": 10.017771,
#     "disk-io": 17.706046,
#     "fibonacci": 17.387075,
#     "network-io": 29.186283,
#     "pi": 16.154195,
#     "pbkdf2": 15.793819,
# }

FUNC_EXEC_TIMES = {}
for fn, fi in TIMELINE_DICT.items():
    FUNC_EXEC_TIMES[fn] = fi[0]

PROCESS_BLOCK_TIME = 4
PROCESS_BLOCK_TIME_WRAP1 = 8

PROCESS_START_TIME = 13

NUM_PROCESS_WRAP1 = 6

THREADS_LATS = {}

def get_threads_lat(fs, task_fn_mp):
    global THREADS_LATS
    thread_lists = [task_fn_mp[f] for f in fs]
    thread_lists_str = ",".join(thread_lists)
    if thread_lists_str in THREADS_LATS:
        return THREADS_LATS[thread_lists_str]
    else:
        thread_lat = threads_predictor(thread_lists)
        THREADS_LATS[thread_lists_str] = thread_lat
        return thread_lat

def get_process_lat(fs, task_fn_mp, index, isMain):
    block_time = index * PROCESS_BLOCK_TIME
    start_time = 0
    if not isMain:
        start_time += PROCESS_START_TIME
    exec_time = get_threads_lat(fs, task_fn_mp)

    return block_time + start_time + exec_time

def predict(partitions, task_fn_mp, isWrap1=False):
    workflow_lat = 0
    for stage_partition in partitions:
        if len(stage_partition) == 1:
            if len(stage_partition[0]) == 1:
                workflow_lat += FUNC_EXEC_TIMES[task_fn_mp[stage_partition[0][0]]]
            else:
                workflow_lat += get_process_lat(stage_partition[0], task_fn_mp, 0, True)
        else:
            process_lats = []
            for i, fs in enumerate(stage_partition[1:]):
                process_lat = get_process_lat(fs, task_fn_mp, i, False)
                process_lats.append(process_lat)

            main_process_lat = get_process_lat(stage_partition[0], task_fn_mp, len(stage_partition)-1, True)
            if isWrap1:
                main_process_lat += len(process_lats) * PROCESS_BLOCK_TIME_WRAP1

            process_lats.append(main_process_lat)

            workflow_lat += max(process_lats)

    return workflow_lat

def get_sorted_fs(fs, task_fn_mp):
    res = []
    for f in fs:
        res.append((f, FUNC_EXEC_TIMES[task_fn_mp[f]]))

    res.sort(key=lambda x: x[1], reverse=True)
    
    return [r[0] for r in res]