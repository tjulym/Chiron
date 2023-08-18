import copy
THREAD_BLOCK = 0.6
THREAD_INIT = 0.8

INTERVAL = 5

THRESHOLD = 1.1
SWITCH_OVERHEAD = 0.005

# PROCESS_BLOCK_TIME = 4
PROCESS_BLOCK_TIME = 0.06
PROCESS_START_TIME = 13
# PROCESS_START_TIME = 43 # FINRA-200

# 2.1707742324222568,ioctl,0.019
# 2.6402720354381914,sendto,0.041999999999999996
# 2.723243170296273,sendto,0.044
# 2.813537010769622,ioctl,0.026
# 2.92833375704528,recvfrom,XXX
# XXX,close,0.083

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

# too many processes in one wrap can result in long load time for a function even in process pool (e.g., FINRA-200)
def get_load_time(index):
    # return min(0.11 * index + 7.87, 13)
    return 0
    return 0.05 * index + 60 # FINRA-200

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
    lat = float(lines[0]) + THREAD_INIT - THREAD_BLOCK
    timelines = []
    for line in lines[1:]:
        _, timestamp, _, exec_time = line.split(",")
        timestamp = float(timestamp) + THREAD_INIT - THREAD_BLOCK
        exec_time = float(exec_time)
        timelines.append([timestamp, exec_time])
    # return lat, timelines

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
    #print("select in", alt_thread_lists)
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

def predict(funcs, indexes):
    # print(funcs, indexes)
    features = {}
    suspended_threads = []
    io_block_threads = []
    thread_lists = {}

    min_index = min(indexes)

    work_thread = None

    for i, f in enumerate(funcs):
        lat, timeline = get_timeline(f)
        # print(f, lat, timeline)
        target_func_name = f
        while target_func_name in features:
            target_func_name = "%s_2" %  target_func_name

        thread_lists[target_func_name] = 0

        if indexes[i] == min_index:
            work_thread = target_func_name
            block_time = indexes[i] * PROCESS_BLOCK_TIME + get_load_time(indexes[i])
            lat += block_time
            for j in range(len(timeline)):
                timeline[j][0] = timeline[j][0] + block_time
        else:
            block_time = indexes[i] * PROCESS_BLOCK_TIME + get_load_time(indexes[i])

            lat += block_time
            for j in range(len(timeline)):
                timeline[j][0] = timeline[j][0] + block_time
            timeline.insert(0, [0, block_time])
            io_block_threads.append([target_func_name, block_time])

        features[target_func_name] = {"lat": lat, "timeline": timeline, "time": 0}

    overall_lat = 0
    # work_thread = funcs[0]
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
                exec_time = max(features[work_thread]["lat"] - features[work_thread]["time"], 0)
                remove_thread(thread_lists, work_thread)
                if len(thread_lists) == 0:
                    overall_lat += exec_time
                    break
        #print(thread_lists)
        # print("exec_time:", work_thread, exec_time)

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

    # return overall_lat
    return overall_lat

if __name__ == '__main__':
    # print(predict(['marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume', 
    #     'marketdata-y', 'lastpx', 'side', 'trddate', 'volume'], [0, 20, 40, 10, 30, 1, 21, 41, 11, 31, 2, 22, 42, 12, 32, 3, 23, 43, 13, 33, 4, 24, 44, 14, 34, 5, 25, 45, 15, 35, 6, 26, 46, 16, 36, 7, 27, 47, 17, 37, 8, 28, 48, 18, 38, 9, 29, 49, 19, 39]))

    print(predict(["upload-user-mentions", "upload-creator", "upload-unique-id", "upload-text", "upload-media"], 
        [0, 1, 0, 1, 0]))
    # print(predict(["upload-home-timeline", "upload-user-timeline", "post-storage"], 
    #     [0, 1, 1]))
    # print(predict(["pi", "pi"], [0, 0]))
