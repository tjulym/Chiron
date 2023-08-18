import threading
import multiprocessing as mp
import psutil
import json
import time
from function.fibonacci_handler import handle as fibonacci
from function.network_io_handler import handle as network_io
from function.disk_io_handler import handle as disk_io
from function.factorial_handler import handle as factorial
from function.pi_handler import handle as pi
from function.pbkdf2_handler import handle as pbkdf2

def run(f, event, index, conn):
	#psutil.Process().cpu_affinity([index])
	result = f(event)
	conn.send(result)
	conn.close()
    
def handle(req):
	start = time.time()

	ps = []	
	parent_conns = []
	for i, f in enumerate([network_io, factorial, disk_io, fibonacci]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[f, req, i, child_conn]))	

	for p in ps:
		p.start()

	for p in ps:
		p.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.append(parent_conn.recv())

	parallel_res = json.dumps(parallel_res)

	ps = []
	parent_conns = []
	for i, f in enumerate([network_io, pi, pbkdf2]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[f, parallel_res, i, child_conn]))

	for p in ps:
		p.start()

	for p in ps:
		p.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.append(parent_conn.recv())

	parallel_res = json.dumps(parallel_res)

	result = {"result": parallel_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

