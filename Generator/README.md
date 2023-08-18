# Generator

`Generator` produces the orchestrator code of `wraps` based on the result of `Scheduler`. It serves as the the function entry (e.g., `handler.py` of the python template in `OpenFaaS`), and uses the `psutil` library to set CPU affinity for each process to isolate resources within a `wrap`.

We provide implementations for native threads, Intel MPK and process pool, respectively.

* [Native threads](https://github.com/tjulym/Chiron/tree/main/Generator/native)
* Intel MPK
  + [MPK-S](https://github.com/tjulym/Chiron/tree/main/Generator/mpk-s)
  + [MPK-L](https://github.com/tjulym/Chiron/tree/main/Generator/mpk-l)
* [Process Pool](https://github.com/tjulym/Chiron/tree/main/Generator/pp)