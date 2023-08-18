# Generator-MPK-S

This module is the implementation of `Generator` with Intel MPK for [small workflows](https://github.com/tjulym/Chiron/blob/main/Scheduler/mpk-s/README.md).

## Start
`Generator` serves as a web service using `Flask`. The following command can start the `Generator` service which is bound to the local port of `20235`:
```
python3 index.py &
```

## Wrap code
We provide a script to submit the `wraps` (i.e., the result of [`Scheduler-MPK-S`](https://github.com/tjulym/Chiron/blob/main/Scheduler/mpk-s/README.md)) to `Generator-MPK-S` as follows:
```
python3 client.py <wraps>
```
Then, the client will send requests to `Generator-MPK-S` and save the returned orchestrator code in `wraps` directory.

For example, if we want the `wrap` codes of `Social Network`, we can execute command as follows:
```
python3 client.py '{"workflow": "sn", "wraps": [[["ComposePost"]], [["UploadText", "UploadMedia", "UploadUserMentions"], ["UploadCreator", "UploadUniqueId"]], [["ComposeAndUpload"]], [["PostStorage"], ["UploadHomeTimeline"], ["UploadUserTimeline"]]]}'
```
And the returned codes of `wrap` are saved in `wraps/sn-wrap.py`.