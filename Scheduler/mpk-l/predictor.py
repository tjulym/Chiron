import json
from CFS import predict as threads_predictor

FUNC_EXEC_TIMES = {
'compose-post': 0.121996, 'upload-user-mentions': 14.2651, 'upload-creator': 13.215116, 
'upload-media': 0.380701, 'upload-text': 1.63713, 'upload-unique-id': 0.651283, 'compose-and-upload': 0.320979, 
'post-storage': 17.879182, 'upload-home-timeline': 23.959915000000002, 'upload-user-timeline': 21.312566999999998, 

'compose-review': 0.10739, 'upload-user-id': 13.996032999999999, 'upload-movie-id': 14.039929, 'mr-upload-text': 0.31925, 
'mr-upload-unique-id': 0.605604, 'mr-compose-and-upload': 0.230004, 'store-review': 18.517567, 'upload-user-review': 19.946811, 
'upload-movie-review': 20.073351, 

'marketdata': 109, 'lastpx': 0.735458, 'side': 0.722307, 'trddate': 0.772194, 'volume': 0.730984, 'margin-balance': 0.807867, 'factorial': 32.017770999999996, 'disk-io': 17.706046, 'fibonacci': 17.387075, 'network-io': 50.186283, 'pi': 31.154195, 'pbkdf2': 15.793819}


PROCESS_BLOCK_TIME = 7

PROCESS_START_TIME = 13

RPC_OVERHEAD = 20
REMOTE_OVERHEAD = 4

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

def get_process_lat(fs, task_fn_mp):
    exec_time = get_threads_lat(fs, task_fn_mp)

    return RPC_OVERHEAD + exec_time + 2

def predict(partitions, task_fn_mp, isWrap1=False):
    workflow_lat = 0
    for stage_partition in partitions:
        if len(stage_partition) == 1:
            if len(stage_partition[0]) == 1:
                # workflow_lat += FEATURES[task_fn_mp[stage_partition[0][0]]][-1] * 1000
                workflow_lat += FUNC_EXEC_TIMES[task_fn_mp[stage_partition[0][0]]]
            else:
                workflow_lat += get_process_lat(stage_partition[0], task_fn_mp)
        else:
            process_lats = []
            for i, fs in enumerate(stage_partition[1:]):
                process_lat = get_process_lat(fs, task_fn_mp)
                process_lats.append(process_lat)

            main_process_lat = get_process_lat(stage_partition[0], task_fn_mp)
            if isWrap1:
                main_process_lat += len(process_lats) * REMOTE_OVERHEAD

            process_lats.append(main_process_lat)

            workflow_lat += max(process_lats)

    return workflow_lat

def get_sorted_fs(fs, task_fn_mp):
    res = []
    for f in fs:
        # res.append((f, FEATURES[task_fn_mp[f]][-1]))
        res.append((f, FUNC_EXEC_TIMES[task_fn_mp[f]]))

    res.sort(key=lambda x: x[1], reverse=True)
    
    return [r[0] for r in res]