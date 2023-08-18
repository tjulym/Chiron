# Scheduler-ProcessPool

This module is the implementation of `Scheduler` with process pool instead of starting new processes for each request. In this implementation, all functions execute in the form of process within a single `wrap`, but each process is bound to a specific CPU through `psutil` for resource efficiency.

## Start
`Scheduler` serves as a web service using `Flask`. The following command can start the `Scheduler` service which is bound to the local port of `20233`:
```
python3 index.py &
```

## Schedule
We can submit the workflow name and SLO to `Scheduler` as follows:
```
curl -d '{"workflow": "<workflow_name>", "SLO": <SLO_in_millisecond>}' http://127.0.0.1:20233/
```
Then, the `Scheduler` will return the `wrap`. 

The available workflows include `sn`, `mr`, `SLApp`, `SLApp-V`, `finra5`, `finra50`, `finra100` and `finra200`.
For example, if we want the `wrap` of `Social Network` with SLO 40 milliseconds, we can execute command as follows:
```
curl -d '{"workflow": "sn", "SLO": 40}' http://127.0.0.1:20233/
```
And we can get the return:
```
{
  "workflow": "sn", 
  "wraps": 
  [
   [
    ["ComposePost"]
   ], 
   [
    ["UploadUserMentions", "UploadMedia", "UploadUniqueId"], 
    ["UploadCreator", "UploadText"]
   ], 
   [
    ["ComposeAndUpload"]
   ], 
   [
    ["PostStorage", "UploadUserTimeline"], 
    ["UploadHomeTimeline"]
   ]
  ]
}
```
This return value indicates that there are 2 CPUs used for `wrap` of `Social Network`. For example, In the stage 2, function (i.e., process) `UploadUserMentions`, `UploadMedia` and `UploadUniqueId` share the same CPU, and function `UploadCreator` and `UploadText` share another.