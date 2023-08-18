import os

THREAD_BLOCK = 0.6
THREAD_INIT = 0.8

INTERVAL = 5

THRESHOLD = 1.1
SWITCH_OVERHEAD = 0.005

TIMELINE_DICT = {}

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
    return lat, timelines

def get_all_timelines():
    global TIMELINE_DICT
    for filename in os.listdir("timelines"):
        func_name = filename.split(".")[0]
        lat, timeline = get_timeline(func_name)
        TIMELINE_DICT[func_name] = (lat, timeline)

get_all_timelines()

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

def predict(funcs):
    features = {}
    new_threads = []
    suspended_threads = []
    io_block_threads = []
    for f in funcs:
        # lat, timeline = get_timeline(f)
        lat, timeline = TIMELINE_DICT[f]
        target_func_name = f
        while target_func_name in features:
            target_func_name = "%s_2" %  target_func_name
        features[target_func_name] = {"lat": lat, "timeline": timeline, "time": 0}
        new_threads.append([target_func_name, THREAD_BLOCK])

    overall_lat = 0
    thread_lists = {"main": 0}
    work_thread = "main"
    switch_count = 0
    while True:
        switch_count += 1
        if work_thread == "main":
            #print("Turn to %s" % "main")
            if len(new_threads) == len(funcs):
                available_time = 9999
            else:
                available_time = INTERVAL
            exec_time = 0
            while len(new_threads) > 0 and exec_time < available_time:
                if not (exec_time + new_threads[0][1] > available_time):
                    available_time = INTERVAL
                    thread_lists[new_threads[0][0]] = 0
                    exec_time += new_threads[0][1]
                    new_threads = new_threads[1:]
                    if len(new_threads) == 0:
                        remove_thread(thread_lists, "main")
                else:
                    new_threads[0][1] = new_threads[0][1] - (available_time - exec_time)
                    exec_time = available_time
            if "main" in thread_lists:
                thread_lists["main"] += exec_time
            except_threads = ["main"]
            io_over_threads = []
            update_status(exec_time, except_threads, io_block_threads, io_over_threads, features)
                
            overall_lat += exec_time
            work_thread = select_thread(thread_lists, except_threads)
            #print("exec_time:", exec_time)
        else:
            #print("Turn to %s" % work_thread)
            if len(thread_lists) == 1:
                #print("exec_time:", features[work_thread]["lat"] - features[work_thread]["time"])
                overall_lat += (features[work_thread]["lat"] - features[work_thread]["time"])
                break                
             
            available_time = INTERVAL
            if len(thread_lists) == len(io_block_threads) + 1:
                available_time += min([ibt[1] for ibt in io_block_threads])
 
            if len(features[work_thread]["timeline"]) > 0:
                #print("timeline: {}; time: {}".format(features[work_thread]["timeline"][0], features[work_thread]["time"]))
                if features[work_thread]["time"] + available_time < features[work_thread]["timeline"][0][0]:
                    exec_time = available_time
                else:
                    exec_time = features[work_thread]["timeline"][0][0] - features[work_thread]["time"]
                    io_block_threads.append([work_thread, features[work_thread]["timeline"][0][1]])
            else:
                #print("lat: {}; time: {}".format(features[work_thread]["lat"], features[work_thread]["time"]))
                if features[work_thread]["time"] + available_time < features[work_thread]["lat"]:
                    exec_time = available_time
                else:
                    exec_time = features[work_thread]["lat"] - features[work_thread]["time"]
                    remove_thread(thread_lists, work_thread)
                    if len(thread_lists) == 0:
                        overall_lat += exec_time
                        break
            #print(thread_lists)
            #print("exec_time:", exec_time)

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
                #print("blocks:", io_block_threads)
                exec_time = io_block_threads[0][1]
                work_thread = io_block_threads[0][0]

                features[work_thread]["timeline"] = features[work_thread]["timeline"][1:]
                features[work_thread]["time"] = features[work_thread]["time"] + exec_time

                io_block_threads = io_block_threads[1:]
                for i in range(len(io_block_threads)):
                    io_block_threads[i][1] = io_block_threads[i][1] - exec_time
                    features[io_block_threads[i][0]]["time"] = features[io_block_threads[i][0]]["time"] + exec_time                    
                overall_lat += exec_time

    return overall_lat + switch_count * SWITCH_OVERHEAD
 
if __name__ == '__main__':
    #predict(["upload-user-mentions", "upload-creator"])
    #print(predict(["upload-user-mentions", "upload-creator", "upload-unique-id"]))
    #print(predict(['upload-creator', 'upload-unique-id', 'upload-user-mentions', 'upload-text', 'upload-media']))
    #print(predict(['post-storage', 'upload-home-timeline', 'upload-user-timeline']))
    #print(predict(['mr-upload-text', 'upload-user-id', 'upload-movie-id', 'mr-upload-unique-id']))
    #print(predict(['fibonacci', 'disk-io', 'factorial', 'network-io']))
    # print(predict(['pi', 'fibonacci', 'pi']))
    # print(predict(['upload-media']))
    print(predict(['marketdata', 'marketdata', 'marketdata']))
