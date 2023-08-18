import threading
import multiprocessing as mp
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

Pools = ProcessPoolExecutor(max_workers=5)

def run(f, event, index):
	psutil.Process().cpu_affinity([index])
	result = f(event)
	return result

class MyThread(threading.Thread):
	def __init__(self, func, args=()):
		threading.Thread.__init__(self)
		self.func = func
		self.args = args

	def run(self):
		self.result = self.func(*self.args)

	def recv(self):
		try:
			return self.result
		except Exception:
			return None

def runt(f, event):
	result = f(event)
	return result
    
def handle(req):
	start = time.time()

	#psutil.Process().cpu_affinity([0])

	p = Pools.submit(run, disk_io, req, 0)

	disk_io_res = p.result()

	ps = []	
	indexs = [0, 1]
	funcs = [fibonacci, factorial]
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, disk_io_res, i))	

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	ps = []
	indexs = [0, 1, 2, 2, 3]
	funcs = [network_io, fibonacci, pi, pi, pbkdf2]
	for i, f in zip(indexs, funcs):
		ps.append(Pools.submit(run, f, parallel_res, i))

	parallel_res = []
	for p in ps:
		parallel_res.append(p.result())

	parallel_res = json.dumps(parallel_res)

	p = Pools.submit(run, factorial, parallel_res, 0)

	factorial_res = p.result()

	p = Pools.submit(run, fibonacci, factorial_res, 0)

	fibonacci_res = p.result()

	result = {"result": fibonacci_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

