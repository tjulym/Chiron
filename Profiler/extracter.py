import re

block_syscalls = ["accept", "close", "creat", "dmi", "fcntl",
    "fsync", "getmsg", "getpmsg", "ioctl", "lockf", "mq_open",
    "msgsnd", "msgrcv", "msync", "nanosleep", "open", "pause",
    "poll", "putmsg", "putpmsg", "read", "readv", "pread",
    "recv", "recvfrom", "recvmsg", "select", "semget", "semctl",
    "semop", "send", "sendto", "sendmsg", "sginap", "write",
    "writev", "pwrite", "openat"]

def format(line, start, end, unfinished):
    if "exit(0)" in line or "exited with 0" in line or "detached" in line:
        return ""
    splits = re.split(r"[ ]+", line)
    pid = splits[0]
    timestamp = (float(splits[1]) - start) * 1000
    syscall = splits[2].split("(")[0]

    if start + timestamp > end:
        return ""
        
    if "unfinished" in line:
        unfinished[pid] = timestamp
        return ""
    elif "resumed" in line:
        syscall = splits[3].strip()
        time = timestamp - unfinished[pid] + float(splits[-1].strip()[1:-1])*1000
        timestamp = unfinished.pop(pid)
    else:
        time = float(splits[-1].strip()[1:-1]) * 1000
    data = [pid, timestamp, syscall, time]
    return data

def get_dup(block_lines):
    for i in range(len(block_lines)):
        for j in range(i+1, len(block_lines)):
            if not block_lines[j][1] > block_lines[i][1]+block_lines[i][3]:
                return (i, j)
    return (0, 0)

def remove_dup(block_lines):
    i1, i2 = get_dup(block_lines)
    if i1 == 0 and i2 == 0:
        return
    while True:
        if not block_lines[i2][1]+block_lines[i2][3] > block_lines[i1][1]+block_lines[i1][3]:
            block_lines.pop(i2)
        else:
            block_lines[i1][3] = block_lines[i2][1]+block_lines[i2][3] - block_lines[i1][1]
            block_lines.pop(i2)
        i1, i2 = get_dup(block_lines)
        if i1 == 0 and i2 == 0:
            return

def scale_down(func_name, block_lines, latency, target_latency):
    if not target_latency < latency:
        return
    
    io_time = sum([block_line[3] for block_line in block_lines])
    if io_time > target_latency:
       return
    scale_per = (target_latency - io_time)/(latency - io_time)
    cpu_times = []
    for i in range(len(block_lines)):
        if i == 0:
            cpu_times.append(block_lines[i][1])
        else:
            cpu_times.append(block_lines[i][1] - block_lines[i-1][1] - block_lines[i-1][3])
    for i in range(len(block_lines)):
        if i == 0:
            block_lines[i][1] = cpu_times[i] * scale_per
        else:
            block_lines[i][1] = block_lines[i-1][1] + block_lines[i-1][3] + cpu_times[i] * scale_per

def get_timeline(func_name, start, end, solo_lat):
    latency = end - start

    with open(f"straces/{func_name}.csv", "r") as f:
        raw_lines = f.readlines()

    block_lines = []
    io_times = 0
    unfinished = {}
    for line in raw_lines:
        format_line = format(line, start, end, unfinished)
        if (not format_line == "") and format_line[1] > 0 and (not format_line[1]+format_line[3] > latency):
            if format_line[2] in block_syscalls:
                block_lines.append(format_line)
    block_lines.sort(key=lambda x: x[1])

    remove_dup(block_lines)
    scale_down(func_name, block_lines, latency, solo_lat)

    res = [min(latency, solo_lat)]

    for line in block_lines:
        res.append(",".join([str(i) for i in line]))

    with open(f"timelines/{func_name}.csv", "w") as f:
        f.writelines(res)