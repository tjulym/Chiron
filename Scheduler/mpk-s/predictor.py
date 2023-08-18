import json
from CFS import predict as process_predictor

FUNC_EXEC_TIMES = {
'compose-post': 0.121996, 'upload-user-mentions': 14.2651, 'upload-creator': 13.215116, 
'upload-media': 0.380701, 'upload-text': 1.63713, 'upload-unique-id': 0.651283, 'compose-and-upload': 0.320979, 
'post-storage': 17.879182, 'upload-home-timeline': 23.959915000000002, 'upload-user-timeline': 21.312566999999998, 

'compose-review': 0.10739, 'upload-user-id': 13.996032999999999, 'upload-movie-id': 14.039929, 'mr-upload-text': 0.31925, 
'mr-upload-unique-id': 0.605604, 'mr-compose-and-upload': 0.230004, 'store-review': 18.517567, 'upload-user-review': 19.946811, 
'upload-movie-review': 20.073351, 

'marketdata': 109, 'lastpx': 0.735458, 'side': 0.722307, 'trddate': 0.772194, 'volume': 0.730984, 'margin-balance': 0.807867, 'factorial': 32.017770999999996, 'disk-io': 17.706046, 'fibonacci': 17.387075, 'network-io': 50.186283, 'pi': 31.154195, 'pbkdf2': 15.793819}


FUNC_INDEX = {}

# PROCESS_BLOCK_TIME = 6.4
PROCESS_BLOCK_TIME = 4
# PROCESS_START_TIME = 14.2
PROCESS_START_TIME = 10

# THREAD_BLOCK_TIME = 1
# THREAD_START_TIME = 1

RECV_OVERHEAD = 1

def get_process_lat(fs, task_fn_mp):
    funcs = []
    indexs = []
    for f in fs:
        funcs.append(task_fn_mp[f])
        indexs.append(FUNC_INDEX[f])

    return process_predictor(funcs, indexs)

def init(stages, task_fn_mp):
    global FUNC_INDEX
    for fs in stages:
        sorted_fs = get_sorted_fs(fs, task_fn_mp)
        # print(", ".join(sorted_fs))
        for i, f in enumerate(sorted_fs):
            FUNC_INDEX[f] = i

def predict(partitions, task_fn_mp):
    workflow_lat = 0
    for stage_partition in partitions:
        if len(stage_partition) == 1:
            if len(stage_partition[0]) == 1:
                workflow_lat += FUNC_EXEC_TIMES[task_fn_mp[stage_partition[0][0]]]
            else:
                workflow_lat += get_process_lat(stage_partition[0], task_fn_mp) + len(stage_partition[0]) * RECV_OVERHEAD
        else:
            process_lats = []
            num_fs = 0
            for fs in stage_partition:
                process_lat = get_process_lat(fs, task_fn_mp)
                process_lats.append(process_lat)
                num_fs += len(fs)

            workflow_lat += max(process_lats) + num_fs * RECV_OVERHEAD

    return workflow_lat

def get_sorted_fs(fs, task_fn_mp):
    res = []
    for f in fs:
        res.append((f, FUNC_EXEC_TIMES[task_fn_mp[f]]))

    res.sort(key=lambda x: x[1], reverse=True)
    
    return [r[0] for r in res]