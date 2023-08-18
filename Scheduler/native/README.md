# Scheduler-Native

This module is the implementation of `Scheduler` with native threads.

## Start
`Scheduler` serves as a web service using `Flask`. The following command can start the `Scheduler` service which is bound to the local port of `20230`:
```
python3 index.py &
```

## Schedule
We can submit the workflow name and SLO to `Scheduler` as follows:
```
curl -d '{"workflow": "<workflow_name>", "SLO": <SLO_in_millisecond>}' http://127.0.0.1:20230/
```
Then, the `Scheduler` will return the `wraps`.

The available workflows include `sn`, `mr`, `SLApp`, `SLApp-V`, `finra5`, `finra50`, `finra100` and `finra200`.
For example, if we want the `wraps` of `FINRA-100` with SLO 350 milliseconds, we can execute command as follows:
```
curl -d '{"workflow": "finra100", "SLO": 350}' http://127.0.0.1:20230/
```
And we can get the return:
```
{
    "workflow": "finra100", 
    "wraps": [
      [
       [["marketdata12", "trddate19", "trddate8", "trddate7", "trddate9", "trddate18", "lastpx14", "lastpx10", "lastpx4", "lastpx15"], 
        ["marketdata10", "marketdata", "trddate16", "trddate5", "lastpx", "volume19", "side9", "side3", "side14"], 
        ["marketdata19", "marketdata8", "trddate14", "trddate3", "lastpx9", "volume16", "side6", "side16", "side"], 
        ["marketdata2", "marketdata17", "trddate12", "trddate", "lastpx8", "lastpx19", "volume15", "side5", "side12"], 
        ["marketdata4", "marketdata15", "lastpx6", "lastpx17", "volume12", "volume", "side2", "side8", "side19"], 
        ["marketdata13", "trddate10", "volume4", "volume3", "volume20", "volume10", "volume5", "volume18", "volume7"]],

       [["marketdata16", "marketdata3", "trddate17", "trddate6", "lastpx13", "lastpx2", "volume8", "side4", "side15"],
        ["marketdata6", "marketdata20", "trddate4", "trddate15", "lastpx11", "volume9", "volume6", "volume17", "side13"],
        ["marketdata9", "marketdata18", "trddate2", "trddate13", "lastpx3", "lastpx20", "side17", "side10", "side11"], 
        ["lastpx12", "marketdata7", "trddate11", "volume2", "lastpx7", "side20", "lastpx18", "marketdata5", "volume13"], 
        ["volume14", "marketdata11", "lastpx16", "volume11", "side18", "trddate20", "side7", "marketdata14", "lastpx5"]]], 

    [[["CheckMarginBalance"]]]]
}
```
This return value indicates that there are two `wraps` for `FINRA-100`. `Wrap1` contains 6 processes of stage 1 (i.e., function `marketdata12` to `volume7`) and all functions of stage 2 (i.e., function `CheckMarginBalance`). And `wrap2` contains 5 processes of stage 1 (i.e., function `marketdata16` to `lastpx5`).