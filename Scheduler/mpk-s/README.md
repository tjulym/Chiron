# Scheduler-MPK-S

This module is the implementation of `Scheduler` with Intel MPK for small workflows, where all functions can be deployed in only 1 `wrap`, e.g., the max degree of parallelism is not more than 6 in our environment.

In this implementation, parallel functions all execute in the form of process, but need to share CPU with others instead of per CPU per process in Chiron with native thread implementation.

Note that, we need to re-profile all functions because Intel MPK incur more instructions and performance degradation.

## Start
`Scheduler` serves as a web service using `Flask`. The following command can start the `Scheduler` service which is bound to the local port of `20231`:
```
python3 index.py &
```

## Schedule
We can submit the workflow name and SLO to `Scheduler` as follows:
```
curl -d '{"workflow": "<workflow_name>", "SLO": <SLO_in_millisecond>}' http://127.0.0.1:20231/
```
Then, the `Scheduler` will return the `wraps`.

The available workflows include `sn`, `mr`, `SLApp`, `SLApp-V` and `finra5`.
For example, if we want the `wraps` of `Social Network` with SLO 85 milliseconds, we can execute command as follows:
```
curl -d '{"workflow": "sn", "SLO": 85}' http://127.0.0.1:20231/
```
And we can get the return:
```
{
  "workflow": "sn", 
  "wraps": 
    [
     [["ComposePost"]], 
     [["UploadUserMentions", "UploadMedia", "UploadText"], ["UploadCreator", "UploadUniqueId"]], 
     [["ComposeAndUpload"]], 
     [["UploadHomeTimeline", "PostStorage"], ["UploadUserTimeline"]]
    ]
}
```
This return value indicates that there are 2 CPUs used for `wrap` of `Social Network`. For example, In the stage 2, function `UploadUserMentions`, `UploadMedia` and `UploadText` share the same CPU, and function `UploadCreator` and `UploadUniqueId` share another.