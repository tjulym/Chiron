from concurrent.futures import ProcessPoolExecutor
import psutil
import json
import time
from function.fibonacci_handler import handle as fibonacci
from function.network_io_handler import handle as network_io
from function.disk_io_handler import handle as disk_io
from function.factorial_handler import handle as factorial
from function.pi_handler import handle as pi
from function.pbkdf2_handler import handle as pbkdf2

Pools = ProcessPoolExecutor(max_workers=4)

def run(f, event, index):
	psutil.Process().cpu_affinity([index])
	result = f(event)
	return result

def handle(req):
	start = time.time()

	#psutil.Process().cpu_affinity([0])

	ps = []
	indexs = [0, 1, 1, 0]
	funcs = [network_io, disk_io, fibonacci, factorial]	
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, req, i))

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	ps = []
	indexs = [0, 1, 1]
	funcs = [network_io, pi, pbkdf2]
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, parallel_res, i))	

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	result = {"result": parallel_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

