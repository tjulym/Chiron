# Profiler

`Profiler` utilizes the `strace` syscall to extract the block periods from block syscalls invoked during function execution, such
as `open`, `read`, `write`, `poll`, `select`, `sendto`, and others. The information collected by `Profiler` includes function latency, start and end timestamp of each block syscall during function execution. And these data will be used in `Predictor`.

Note that, the following script should be executed by root user due to permission issues.

## Profile
We provide a script to profile a given function directly, but make sure that the target function Pod runs in current worker node.
```
python3 profile.py <function_name>
```
This script will save the logs of `strace` in `straces/<function_name.csv>`, and results of profiling in `timelines/<function_name.csv>`.

The supported functions are as follows:
* Social Network: `compose-post`, `upload-media`, `upload-creator`, `upload-text`, `upload-user-mentions`, `upload-unique-id`, 
    `compose-and-upload`, `post-storage`, `upload-user-timeline` and `upload-home-timeline`
* Movie Reviewing: `compose-review`, `upload-user-id`, `upload-movie-id`, `mr-upload-text`, `mr-upload-unique-id`, 
    `mr-compose-and-upload`, `store-review`, `upload-user-review` and `upload-movie-review`
* SLApp: `marketdata`, `lastpx`, `side`, `trddate`, `volume` and `margin-balance`
* Financial Industry Regulation (FINRA): `disk-io`, `factorial`, `fibonacci`, `pbkdf2`, `pi` and `network-io`

## Result example
Here are the profiling example of function `side`, i.e., content of `timelines/side.csv`:
```
0.722307
66740,0.02389557853684777,open,0.09536590957142549
66740,0.207095013986014,ioctl,0.01711164010916837
66740,0.31472225389994624,ioctl,0.016296800103969878
66740,0.5070525201721355,read,0.01955616012476385
66740,0.5600890481441636,read,0.016296800103969878
66740,0.6504259913932222,close,0.01711164010916837
```
The first line, i.e., `0.7223` is the latency (millisecond) of function `side`. And the other lines record the block periods of block syscalls. For example, the second line indicates that function `side` (pid is `66740`) calls `open` syscall at `0.024` millisecond and the duration of this block operation, i.e., IO time, is `0.095` millisecond.