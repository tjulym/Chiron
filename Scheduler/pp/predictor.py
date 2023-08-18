import json
from CFS import predict as threads_predictor

FUNC_EXEC_TIMES = {
    "compose-post": 0.121996,
    "upload-user-mentions": 9.765100,
    "upload-creator": 8.815116,
    "upload-media": 0.380701,
    "upload-text": 1.637130,
    "upload-unique-id": 0.651283,
    "compose-and-upload": 0.320979,
    "post-storage": 12.879182,
    "upload-home-timeline": 19.059915,
    "upload-user-timeline": 16.112567,

    "compose-review": 0.107390,
    "upload-user-id": 8.396033,
    "upload-movie-id": 8.539929,
    "mr-upload-text": 0.319250,
    "mr-upload-unique-id": 0.605604,
    "mr-compose-and-upload": 0.230004,
    "store-review": 12.117567,
    "upload-user-review": 14.946811,
    "upload-movie-review": 15.873351,
    
    "marketdata": 92,
    "lastpx": 0.735458,
    "side": 0.722307,
    "trddate": 0.772194,
    "volume": 0.730984,
    "margin-balance": 0.807867,
    "factorial": 10.017771,
    "disk-io": 17.706046,
    "fibonacci": 17.387075,
    "network-io": 29.186283,
    "pi": 16.154195,
    "pbkdf2": 15.793819,
}


# PROCESS_BLOCK_TIME = 4
PROCESS_BLOCK_TIME = 0.05

# PROCESS_START_TIME = 13
PROCESS_START_TIME = 43 #FINRA-200

# THREAD_BLOCK_TIME = 1
# THREAD_START_TIME = 1

RECV_OVERHEAD = 1

THREADS_LATS = {}

def get_process_lat(fs, task_fn_mp, indexes):
    funcs = []
    indexs = []
    for f in fs:
        funcs.append(task_fn_mp[f])
        indexs.append(indexes[f])

    return threads_predictor(funcs, indexs)

def predict(partitions, task_fn_mp, indexes):
    workflow_lat = 0
    for stage_partition in partitions:
        if len(stage_partition) == 1:
            if len(stage_partition[0]) == 1:
                workflow_lat += FUNC_EXEC_TIMES[task_fn_mp[stage_partition[0][0]]]
            else:
                workflow_lat += (get_process_lat(stage_partition[0], task_fn_mp, indexes) + 2)
        else:
            process_lats = []
            for fs in stage_partition:
                process_lat = get_process_lat(fs, task_fn_mp, indexes)
                process_lats.append(process_lat)

            # workflow_lat += (max(process_lats) + 2 +  40)
            workflow_lat += (max(process_lats) + 2)

    return workflow_lat

def get_sorted_fs(partitions, task_fn_mp):
    indexes = {}
    all_fs = []
    for fs in partitions[0]:
        for f in fs:
            all_fs.append((f, FUNC_EXEC_TIMES[task_fn_mp[f]]))

    all_fs.sort(key=lambda x: x[1], reverse=True)

    for i, f in enumerate(all_fs):
        indexes[f[0]] = i

    return indexes
    
