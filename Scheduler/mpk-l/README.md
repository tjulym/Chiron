# Scheduler-MPK-L

This module is the implementation of `Scheduler` with Intel MPK for large workflows, where functions need to be deployed in multiple `wraps`, e.g., the max degree of parallelism is more than 6 in our environment.

In this implementation, parallel functions all execute in the form of process, but all processes within the same `wrap` need to share the same CPU, i.e., per CPU per `wrap` instead of per CPU per process in Chiron with native thread implementation.

Note that, we need to re-profile all functions because Intel MPK incur more instructions and performance degradation.

## Start
`Scheduler` serves as a web service using `Flask`. The following command can start the `Scheduler` service which is bound to the local port of `20232`:
```
python3 index.py &
```

## Schedule
We can submit the workflow name and SLO to `Scheduler` as follows:
```
curl -d '{"workflow": "<workflow_name>", "SLO": <SLO_in_millisecond>}' http://127.0.0.1:20232/
```
Then, the `Scheduler` will return the `wraps`.

The available workflows include `finra50`, `finra100` and `finra200`.
For example, if we want the `wraps` of `FINRA-50` with SLO 348 milliseconds, we can execute command as follows:
```
curl -d '{"workflow": "finra50", "SLO": 348}' http://127.0.0.1:20232/
```
And we can get the return:
```
{
  "workflow": "finra50", 
  "wraps": 
    [
     [
      ["marketdata", "trddate3", "trddate9", "trddate4", "trddate10", "lastpx2", "lastpx8", "lastpx", "lastpx7"], 
      ["marketdata6", "trddate2", "trddate5", "trddate7", "volume4", "volume10", "volume5", "side2", "side9"], 
      ["marketdata7", "marketdata5", "trddate6", "trddate8", "volume9", "volume3", "volume7", "side7"], 
      ["marketdata4", "marketdata10", "trddate", "lastpx5", "volume2", "side3", "side", "side6"], 
      ["marketdata3", "marketdata9", "lastpx10", "lastpx6", "lastpx4", "volume8", "volume", "side5"], 
      ["marketdata2", "marketdata8", "lastpx9", "lastpx3", "volume6", "side8", "side4", "side10"]
     ], 
     [
      ["CheckMarginBalance"]
     ]
    ]
}
```
This return value indicates that there are 6 `wraps` for `FINRA-50`. For example, `Wrap1` contains 9 processes of stage 1 (i.e., function `marketdata` to `lastpx7`) and all functions of stage 2 (i.e., function `CheckMarginBalance`). And `wrap6` contains 8 processes of stage 1 (i.e., function `marketdata2` to `side10`).