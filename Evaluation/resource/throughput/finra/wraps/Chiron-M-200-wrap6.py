import threading
import multiprocessing as mp
import psutil
import json
import time
#from function.margin_balance_handler import handle as margin_balance
from function.trddate_handler import handle as trddate
from function.lastpx_handler import handle as lastpx
from function.volume_handler import handle as volume
from function.side_handler import handle as side
from function.marketdata_handler import handle as marketdata

def run(f, event, index, conn):
	psutil.Process().cpu_affinity([5])
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
	result = f(event)
	return result
    
def handle(req):
	ps = []
	parent_conns = []

	funcs = [marketdata, marketdata, marketdata, trddate, trddate, trddate, lastpx, lastpx, volume, volume, volume, side, side, side]
	for i, f in enumerate(funcs):
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
	return parallel_res

