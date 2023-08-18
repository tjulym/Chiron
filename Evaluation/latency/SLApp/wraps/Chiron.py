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

def run(fs, event, index, conn):
	psutil.Process().cpu_affinity([index])
	ps = []
	for f in fs:
		ps.append(MyThread(runt, args=[f, event]))

	for p in ps:
		p.start()
	for p in ps:
		p.join()

	result = []
	for p in ps:
		result.append(p.recv())
	conn.send(result)
	conn.close()

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

	psutil.Process().cpu_affinity([0])

	ps = []	
	parent_conns = []
	for i, fs in enumerate([[fibonacci, factorial]]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[fs, req, 1+i, child_conn]))	

	ts = []
	for f in [network_io, disk_io]:
		ts.append(MyThread(runt, args=[f, req]))

	for p in ps:
		p.start()

	for t in ts:
		t.start()

	for p in ps:
		p.join()

	for t in ts:
		t.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.extend(parent_conn.recv())

	for t in ts:
		parallel_res.append(t.recv())

	parallel_res = json.dumps(parallel_res)

	ps = []
	parent_conns = []
	for i, f in enumerate([[network_io]]):
		parent_conn, child_conn = mp.Pipe()
		parent_conns.append(parent_conn)
		ps.append(mp.Process(target=run, args=[f, parallel_res, 1+i, child_conn]))

	ts = []
	for f in [pi, pbkdf2]:
		ts.append(MyThread(runt, args=(f, req)))	

	for p in ps:
		p.start()

	for t in ts:
		t.start()

	for p in ps:
		p.join()

	for t in ts:
		t.join()

	parallel_res = []
	for parent_conn in parent_conns:
		parallel_res.extend(parent_conn.recv())

	for t in ts:
		parallel_res.append(t.recv())

	parallel_res = json.dumps(parallel_res)

	result = {"result": parallel_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

