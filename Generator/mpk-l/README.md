# Generator-MPK-L

This module is the implementation of `Generator` with Intel MPK for [large workflows](https://github.com/tjulym/Chiron/blob/main/Scheduler/mpk-l/README.md).

## Start
`Generator` serves as a web service using `Flask`. The following command can start the `Generator-MPK-L` service which is bound to the local port of `20236`:
```
python3 index.py &
```

## Wrap code
We provide a script to submit the `wraps` (i.e., the result of [`Scheduler-MPK-L`](https://github.com/tjulym/Chiron/blob/main/Scheduler/mpk-l/README.md)) to `Generator-MPK-L` as follows:
```
python3 client.py <wraps>
```
Then, the client will send requests to `Generator-MPK-L` and save the returned orchestrator code in `wraps` directory.

For example, if we want the `wraps` codes of `FINRA-50`, we can execute command as follows:
```
python3 client.py '{"workflow": "finra50", "wraps": [[["marketdata", "trddate3", "trddate9", "trddate4", "trddate10", "lastpx2", "lastpx8", "lastpx", "lastpx7"], ["marketdata6", "trddate2", "trddate5", "trddate7", "volume4", "volume10", "volume5", "side2", "side9"], ["marketdata7", "marketdata5", "trddate6", "trddate8", "volume9", "volume3", "volume7", "side7"], ["marketdata4", "marketdata10", "trddate", "lastpx5", "volume2", "side3", "side", "side6"], ["marketdata3", "marketdata9", "lastpx10", "lastpx6", "lastpx4", "volume8", "volume", "side5"], ["marketdata2", "marketdata8", "lastpx9", "lastpx3", "volume6", "side8", "side4", "side10"]], [["CheckMarginBalance"]]]}'
```
And the returned codes of 6 `wraps` are saved in `wraps/finra50-wrap.py`, `wraps/finra50-wrap2.py`, `wraps/finra50-wrap3.py`, `wraps/finra50-wrap4.py`, `wraps/finra50-wrap5.py` and `wraps/finra50-wrap6.py`.