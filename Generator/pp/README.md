# Generator-ProcessPool

This module is the implementation of `Generator` with [process pool](https://github.com/tjulym/Chiron/blob/main/Scheduler/pp/README.md) instead of starting new processes for each request.

## Start
`Generator` serves as a web service using `Flask`. The following command can start the `Generator` service which is bound to the local port of `20237`:
```
python3 index.py &
```

## Wrap code
We provide a script to submit the `wrap` (i.e., the result of [`Scheduler-ProcessPool`](https://github.com/tjulym/Chiron/blob/main/Scheduler/pp/README.md)) to `Generator-ProcessPool` as follows:
```
python3 client.py <wraps>
```
Then, the client will send requests to `Generator-ProcessPool` and save the returned orchestrator code in `wraps` directory.

For example, if we want the `wrap` codes of `Social Network`, we can execute command as follows:
```
python3 client.py '{"workflow": "sn", "wraps": [[["ComposePost"]], [["UploadUserMentions",  "UploadMedia", "UploadUniqueId"], ["UploadCreator", "UploadText"]], [["ComposeAndUpload"]], [["PostStorage", "UploadUserTimeline"], ["UploadHomeTimeline"]]]}'
```
And the returned codes of `wrap` are saved in `wraps/sn-wrap.py`.