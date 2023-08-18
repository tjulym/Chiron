# Generator-Native

This module is the implementation of `Generator` with native threads.

## Start
`Generator` serves as a web service using `Flask`. The following command can start the `Generator` service which is bound to the local port of `20234`:
```
python3 index.py &
```

## Wrap code
We provide a script to submit the `wraps` (i.e., the result of [`Scheduler`](https://github.com/tjulym/Chiron/blob/main/Scheduler/native/README.md)) to `Generator` as follows:
```
python3 client.py <wraps>
```
Then, the client will send requests to `Generator` and save the returned orchestrator code in `wraps` directory.

For example, if we want the `wraps` codes of `FINRA-100`, we can execute command as follows:
```
python3 client.py '{"workflow": "finra100", "wraps": [[[["marketdata12", "trddate19", "trddate8", "trddate7", "trddate9", "trddate18", "lastpx14", "lastpx10", "lastpx4", "lastpx15"], ["marketdata10", "marketdata", "trddate16", "trddate5", "lastpx", "volume19", "side9", "side3", "side14"], ["marketdata19", "marketdata8", "trddate14", "trddate3", "lastpx9", "volume16", "side6", "side16", "side"], ["marketdata2", "marketdata17", "trddate12", "trddate", "lastpx8", "lastpx19", "volume15", "side5", "side12"], ["marketdata4", "marketdata15", "lastpx6", "lastpx17", "volume12", "volume", "side2", "side8", "side19"], ["marketdata13", "trddate10", "volume4", "volume3", "volume20", "volume10", "volume5", "volume18", "volume7"]],[["marketdata16", "marketdata3", "trddate17", "trddate6", "lastpx13", "lastpx2", "volume8", "side4", "side15"],["marketdata6", "marketdata20", "trddate4", "trddate15", "lastpx11", "volume9", "volume6", "volume17", "side13"], ["marketdata9", "marketdata18", "trddate2", "trddate13", "lastpx3", "lastpx20", "side17", "side10", "side11"], ["lastpx12", "marketdata7", "trddate11", "volume2", "lastpx7", "side20", "lastpx18", "marketdata5", "volume13"], ["volume14", "marketdata11", "lastpx16", "volume11", "side18", "trddate20", "side7", "marketdata14", "lastpx5"]]], [[["CheckMarginBalance"]]]]}'
```
And the returned codes of two `wraps` are saved in `wraps/finra100-wrap.py` and `wraps/finra100-wrap2.py`.