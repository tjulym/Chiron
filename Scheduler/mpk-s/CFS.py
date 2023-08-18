THREAD_BLOCK = 0.6
THREAD_INIT = 0.8

INTERVAL = 5

THRESHOLD = 1.1
SWITCH_OVERHEAD = 0.005

# PROCESS_BLOCK_TIME = 6.4
PROCESS_BLOCK_TIME = 3
# PROCESS_START_TIME = 14.2
PROCESS_START_TIME = 11

FUNC_EXEC_TIMES = {
'compose-post': 0.121996, 'upload-user-mentions': 14.2651, 'upload-creator': 13.215116, 
'upload-media': 0.380701, 'upload-text': 1.63713, 'upload-unique-id': 0.651283, 'compose-and-upload': 0.320979, 
'post-storage': 17.879182, 'upload-home-timeline': 23.959915000000002, 'upload-user-timeline': 21.312566999999998, 

'compose-review': 0.10739, 'upload-user-id': 13.996032999999999, 'upload-movie-id': 14.039929, 'mr-upload-text': 0.31925, 
'mr-upload-unique-id': 0.605604, 'mr-compose-and-upload': 0.230004, 'store-review': 18.517567, 'upload-user-review': 19.946811, 
'upload-movie-review': 20.073351, 

'marketdata': 109, 'lastpx': 0.735458, 'side': 0.722307, 'trddate': 0.772194, 'volume': 0.730984, 'margin-balance': 0.807867, 'factorial': 32.017770999999996, 'disk-io': 17.706046, 'fibonacci': 17.387075, 'network-io': 50.186283, 'pi': 31.154195, 'pbkdf2': 15.793819}

def get_dup(timelines):
    for i in range(len(timelines)-1):
        if not timelines[i][0] + timelines[i][1] < timelines[i+1][0]:
            return i
    return -1

def scale(lat, timelines, overhead):
    scale_per = (lat + overhead) / lat
    for i in range(len(timelines)):
        timelines[i][0] = timelines[i][0] * scale_per
        timelines[i][1] = timelines[i][1] * scale_per
    while True:
        dup_index = get_dup(timelines)
        if dup_index == -1:
            break
        timelines[dup_index][1] = timelines[dup_index+1][1] - timelines[dup_index][0]
        timelines.remove(dup_index+1)

def get_timeline(func_name):
    with open("timelines/%s.csv" % func_name, "r") as f:
        lines = f.readlines()
    lat = float(lines[0])
    timelines = []
    for line in lines[1:]:
        _, timestamp, _, exec_time = line.split(",")
        timestamp = float(timestamp)
        exec_time = float(exec_time)
        timelines.append([timestamp, exec_time])
    
    overhead = FUNC_EXEC_TIMES[func_name] - lat
    if overhead > 0:
        scale(lat, timelines, overhead)
    lat += overhead

    return lat, timelines

def remove_thread(thread_lists, target_thread):
    if target_thread not in thread_lists:
        return
    thread_lists.pop(target_thread)

def select_thread(thread_lists, except_threads):
    thread_lists2 = thread_lists.copy()
    for except_thread in except_threads:
        if except_thread in thread_lists2:
            thread_lists2.pop(except_thread)
    if len(thread_lists2) == 0:
        return ""
    alt_thread_lists = list(thread_lists2.items())
    alt_thread_lists.sort(key=lambda x: x[1])
    return alt_thread_lists[0][0]
    
def update_status(exec_time, except_threads, io_block_threads, io_over_threads, features):
    for thread, io_time in io_block_threads:
        if thread == except_threads[0]:
            continue
        if exec_time < io_time:
            except_threads.append(thread)
            features[thread]["time"] = features[thread]["time"] + exec_time
        else:
            io_over_threads.append([thread, io_time])
            features[thread]["time"] = features[thread]["time"] + io_time
            features[thread]["timeline"] = features[thread]["timeline"][1:]
    for thread in io_over_threads:
        io_block_threads.remove(thread)
    for i in range(len(io_block_threads)):
        if io_block_threads[i][0] == except_threads[0]:
            continue
        io_block_threads[i][1] = io_block_threads[i][1] - exec_time

def predict(funcs, indexs):
    features = {}
    suspended_threads = []
    io_block_threads = []
    thread_lists = {}

    min_index = min(indexs)

    for i, f in enumerate(funcs):
        lat, timeline = get_timeline(f)
        target_func_name = f
        while target_func_name in features:
            target_func_name = "%s_2" %  target_func_name
        thread_lists[f] = 0
        if indexs[i] == min_index:
            block_time = indexs[i] * PROCESS_BLOCK_TIME + PROCESS_START_TIME
            lat += block_time
            for j in range(len(timeline)):
                timeline[j][0] = timeline[j][0] + block_time
        else:
            block_time = indexs[i] * PROCESS_BLOCK_TIME + PROCESS_START_TIME
            lat += block_time
            for j in range(len(timeline)):
                timeline[j][0] = timeline[j][0] + block_time
            timeline.insert(0, [0, block_time])
            io_block_threads.append([f, block_time])
        features[target_func_name] = {"lat": lat, "timeline": timeline, "time": 0}

    overall_lat = 0
    work_thread = funcs[0]
    switch_count = 0
    while True:
        switch_count += 1
        # print("Turn to %s" % work_thread)
        if len(thread_lists) == 1:
            # print("exec_time:", features[work_thread]["lat"] - features[work_thread]["time"])
            overall_lat += (features[work_thread]["lat"] - features[work_thread]["time"])
            break                
         
        available_time = INTERVAL
        if len(thread_lists) == len(io_block_threads) + 1:
            available_time += min([ibt[1] for ibt in io_block_threads])

        if len(features[work_thread]["timeline"]) > 0:
            # print("timeline: {}; time: {}".format(features[work_thread]["timeline"][0], features[work_thread]["time"]))
            if features[work_thread]["time"] + available_time < features[work_thread]["timeline"][0][0]:
                exec_time = available_time
            else:
                exec_time = features[work_thread]["timeline"][0][0] - features[work_thread]["time"]
                io_block_threads.append([work_thread, features[work_thread]["timeline"][0][1]])
        else:
            # print("lat: {}; time: {}".format(features[work_thread]["lat"], features[work_thread]["time"]))
            if features[work_thread]["time"] + available_time < features[work_thread]["lat"]:
                exec_time = available_time
            else:
                exec_time = features[work_thread]["lat"] - features[work_thread]["time"]
                remove_thread(thread_lists, work_thread)
                if len(thread_lists) == 0:
                    overall_lat += exec_time
                    break
        #print(thread_lists)
        # print("exec_time:", exec_time)

        if work_thread in thread_lists:
            thread_lists[work_thread] += exec_time
        except_threads = [work_thread]
        io_over_threads = []
        update_status(exec_time, except_threads, io_block_threads, io_over_threads, features)
        features[work_thread]["time"] = features[work_thread]["time"] + exec_time

        overall_lat += exec_time
        work_thread = select_thread(thread_lists, except_threads)

        if work_thread == "":
            io_block_threads.sort(key=lambda x: x[1])
            # print("blocks:", io_block_threads)
            exec_time = io_block_threads[0][1]
            work_thread = io_block_threads[0][0]

            features[work_thread]["timeline"] = features[work_thread]["timeline"][1:]
            features[work_thread]["time"] = features[work_thread]["time"] + exec_time

            io_block_threads = io_block_threads[1:]
            for i in range(len(io_block_threads)):
                io_block_threads[i][1] = io_block_threads[i][1] - exec_time
                features[io_block_threads[i][0]]["time"] = features[io_block_threads[i][0]]["time"] + exec_time                    
            overall_lat += exec_time

    return overall_lat #sum_lats

