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

	parent_conn, child_conn = mp.Pipe()
	p = mp.Process(target=run, args=[disk_io, req, 0, child_conn])

	p.start()
	p.join()

	disk_io_res = parent_conn.recv()

	ps = []	
	parent_conns = []
	for i, f in enumerate([factorial, fibonacci]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[f, disk_io_res, i, child_conn]))	

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
	for i, f in enumerate([network_io, pi, pbkdf2, pi, fibonacci]):
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

	parent_conn, child_conn = mp.Pipe()
	p = mp.Process(target=run, args=[factorial, parallel_res, 0, child_conn])

	p.start()
	p.join()

	factorial_res = parent_conn.recv()

	parent_conn, child_conn = mp.Pipe()
	p = mp.Process(target=run, args=[fibonacci, factorial_res, 0, child_conn])

	p.start()
	p.join()

	fibonacci_res = parent_conn.recv()

	result = {"result": fibonacci_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

