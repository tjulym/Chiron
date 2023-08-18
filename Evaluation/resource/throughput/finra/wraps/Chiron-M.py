import threading
import multiprocessing as mp
import psutil
import json
import time
from function.margin_balance_handler import handle as margin_balance
from function.trddate_handler import handle as trddate
from function.lastpx_handler import handle as lastpx
from function.volume_handler import handle as volume
from function.side_handler import handle as side
from function.marketdata_handler import handle as marketdata
from mpkmemalloc import *

def run(f, event, index, conn):
	#psutil.Process().cpu_affinity([index])
	result = f(event)
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
	pkey_thread_mapper()
	result = f(event)
	pymem_reset()
	return result
    
def handle(req):
	start = time.time()

	pymem_setup_allocators(0)

	psutil.Process().cpu_affinity([0])

	ps = []	
	parent_conns = []
	indexs = [0, 0, 0, 0, 0]
	funcs = [marketdata, trddate, lastpx, volume, side]
	for i, f in zip(indexs, funcs):
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

	p = MyThread(runt, args=[margin_balance, parallel_res])

	p.start()
	p.join()

	margin_balance_res = p.recv()

	margin_balance_res = json.dumps(margin_balance_res)

	pymem_reset_pkru()

	result = {"result": margin_balance_res, "time": {"workflow": {"start": start, "end": time.time()}}}

	return json.dumps(result)

